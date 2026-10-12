# A5
Assignment 5

A bridge that lets an agent (Claude Code) write scripts and run them inside After Effects.

## 1. Which app, and which way

**After Effects 2026, by command.**

`ae-run` uses the macOS `osascript` command to tell After Effects to run a script (`DoScript`). Whatever the script prints comes back to Terminal through a small temporary file.

Tested on a Mac with After Effects 2026 (26.5). It is Mac only, because `osascript` is a macOS command.

## 2. How to run it

You need a Mac with After Effects, Python 3 and git.

1. In Terminal:

   ```
   git clone https://github.com/bshultz-sva/A5.git
   cd A5
   ```

2. Open After Effects. In **Settings > Scripting & Expressions**, turn on **Allow Scripts to Write Files and Access Network**. The bridge never opens After Effects for you; if it is closed, `ae-run` says so and stops.

3. In Terminal, from the A5 folder:

   ```
   ./ae-run examples/hello_ae.jsx
   ```

   The first time, macOS asks whether Terminal may control After Effects. Click **Allow**. Terminal then prints something like this, with your own project's name and comps:

   ```
   Hello from After Effects 26.5x89
   Project: Peanuts.aep
   Comp: Clouds Comp - 2 layers, 1920x1080
   Comp: Comp 1 - 38 layers, 1920x1080
   2 comps in the project
   ```

   This example changes nothing in your project.

4. To run one line instead of a file:

   ```
   ./ae-run -c "print(app.project.numItems)"
   ```

Scripts are ExtendScript (`.jsx`), the scripting language built into After Effects. Inside a script, `print(...)` sends text back to Terminal and `return value` sends back a final value. Everything one script does is a single undo step in After Effects. If a script has an error, the error message and line number come back to Terminal.

### Using it with an agent

Start Claude Code in the A5 folder and tell it: "Run After Effects scripts with `./ae-run`." Then ask for what you want in plain words.

### Using it from Python

`ae_bridge.py` can be imported by any Python script, including one running inside Maya:

```python
import ae_bridge
print(ae_bridge.run('return app.project.numItems + " items in the project"'))
```

## 3. What I asked for, and what happened

These are the exact words I typed to the agent.

**"How can a script send commands to After Effects"**

It explained that After Effects is scripted in ExtendScript, and that on a Mac an outside script can send it commands with `osascript` and `DoScript`. It said it could build a bridge that way.

**"build a bridge from Maya to After Effects"**

It wrote `ae_bridge.py` and `ae-run`. The first version did not work: After Effects ran the scripts but always answered "0" instead of the result. The agent found this by having a script write a small file, then changed the bridge to pass results back through a temporary file. After that, a read-only test reported After Effects 26.5 and my open project, Peanuts.aep, with 44 items. Two tests with mistakes on purpose (one runtime error, one syntax error) both came back to Terminal as plain error messages.

**"create a new composition layer in Peanuts.aep, from layers clouds and moving clounds in Comp1"**

It first listed the layers in Comp 1 without changing anything, then pre-composed "clouds" and "moving clouds" into a new comp called "Clouds Comp". Both layers were locked, so it unlocked them first and re-locked them inside the new comp. The two layers were not next to each other in the stack, so combining them changed the stacking order: "moving clouds" used to be below the ducks layers and is now above them. It did not save the project, and the change was one undo step. The script it ran is in `examples/precompose_clouds.jsx`.

## 4. Recording

https://youtu.be/CGnpY45Z-PE
