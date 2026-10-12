// Test script for the After Effects bridge: reports what is open. It changes nothing.
// Run it from Terminal with:  ./ae-run examples/hello_ae.jsx

print("Hello from After Effects", app.version);
print("Project:", app.project.file ? app.project.file.name : "(not saved yet)");

var comps = 0;
for (var i = 1; i <= app.project.numItems; i++) {
    var item = app.project.item(i);
    if (item instanceof CompItem) {
        comps++;
        print("Comp:", item.name, "-", item.numLayers, "layers,", item.width + "x" + item.height);
    }
}
return comps + " comps in the project";
