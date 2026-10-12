"""Send scripts to After Effects and get back what they printed.

Works from Terminal (see `ae-run`) or from any Python script, including one running in Maya:

    import ae_bridge
    print(ae_bridge.run('print(app.project.numItems + " items in the project")'))
    ae_bridge.run_file("/path/to/script.jsx")

Scripts are written in ExtendScript, After Effects' JavaScript. Inside a script,
print(...) sends text back, and `return value` sends a final value back.
Results come back through a small temporary file, so After Effects needs
"Allow Scripts to Write Files and Access Network" turned on in its
Scripting & Expressions settings.
Everything a script does is one undo step in After Effects.

After Effects has to be open already; this never launches it.
"""
import glob
import json
import os
import subprocess
import tempfile

# Wrapped around every script so that errors come back as text instead of
# stopping After Effects with an error dialog. The script itself goes where
# SOURCE is, so the wrapper's line count before it must match HEADER_LINES.
WRAPPER = """(function () {
    var lines = [];
    function print() {
        var parts = [];
        for (var i = 0; i < arguments.length; i++) { parts.push(String(arguments[i])); }
        lines.push(parts.join(" "));
    }
    var status = "OK";
    app.beginUndoGroup("Script from bridge");
    try {
        var value = (function () {
SOURCE
        })();
        if (value !== undefined) { lines.push(String(value)); }
    } catch (error) {
        status = "ERROR";
        lines.push(error.toString() + (error.line ? " (line " + (error.line - HEADER_LINES) + ")" : ""));
    }
    app.endUndoGroup();
    var result = new File(RESULT);
    result.encoding = "UTF-8";
    result.open("w");
    result.write(status + "\\n" + lines.join("\\n"));
    result.close();
})();
"""
HEADER_LINES = WRAPPER[:WRAPPER.index("SOURCE")].count("\n")

# Runs the wrapped file, and catches the one thing the wrapper can't: a script that won't even parse
LOADER = """(function () {
    try { $.evalFile(WRAPPED); } catch (error) {
        var result = new File(RESULT);
        result.encoding = "UTF-8";
        result.open("w");
        result.write("ERROR\\n" + error.toString() + (error.line ? " (line " + (error.line - HEADER_LINES) + ")" : ""));
        result.close();
    }
})();"""

APPLESCRIPT = """on run arguments
    with timeout of %d seconds
        tell application "%s" to DoScript (item 1 of arguments)
    end timeout
end run"""


class AfterEffectsError(RuntimeError):
    """After Effects couldn't be reached, or the script raised an error there."""


def app_name():
    """The installed After Effects, newest first, e.g. 'Adobe After Effects 2026'."""
    apps = sorted(glob.glob("/Applications/Adobe After Effects */Adobe After Effects *.app"), reverse=True)
    apps = [a for a in apps if "Render Engine" not in a]
    if not apps:
        raise AfterEffectsError("After Effects isn't installed in /Applications.")
    return os.path.basename(apps[0])[:-len(".app")]


def is_open():
    return subprocess.run(["pgrep", "-x", "After Effects"], capture_output=True).returncode == 0


def run(source, timeout=600):
    """Run ExtendScript in After Effects. Returns what it printed; raises AfterEffectsError if it failed."""
    name = app_name()
    if not is_open():
        raise AfterEffectsError("After Effects isn't open. Open it and try again.")

    folder = tempfile.mkdtemp(prefix="ae-run-")
    wrapped, result = os.path.join(folder, "script.jsx"), os.path.join(folder, "result.txt")

    def fill(template):
        return (template.replace("HEADER_LINES", str(HEADER_LINES)).replace("RESULT", json.dumps(result))
                .replace("WRAPPED", json.dumps(wrapped)))

    with open(wrapped, "w", encoding="utf-8") as f:
        f.write(fill(WRAPPER).replace("SOURCE", source))

    done = subprocess.run(["osascript", "-e", APPLESCRIPT % (timeout, name), fill(LOADER)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        problem = done.stderr.strip()
        if "-1743" in problem:
            problem += ("\nmacOS is blocking this. In System Settings > Privacy & Security > Automation, "
                        "allow this app to control After Effects.")
        raise AfterEffectsError("Couldn't reach After Effects: " + problem)

    # After Effects hands results back through a file, which it may only write if this preference is on
    if not os.path.exists(result):
        raise AfterEffectsError(
            "After Effects ran the script but couldn't report back. In After Effects, open Settings > "
            "Scripting & Expressions and turn on \"Allow Scripts to Write Files and Access Network\".")
    with open(result, encoding="utf-8") as f:
        status, _, output = f.read().partition("\n")
    if status != "OK":
        raise AfterEffectsError(output or "After Effects reported an error without a message.")
    return output


def run_file(path, timeout=600):
    """Run a .jsx file in After Effects."""
    with open(path, encoding="utf-8") as f:
        return run(f.read(), timeout=timeout)
