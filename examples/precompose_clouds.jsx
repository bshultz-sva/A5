// The script the agent wrote when I asked for a new composition layer made from
// the "clouds" and "moving clouds" layers of Comp 1 in my project, Peanuts.aep.
// It is here as a record of what ran. It only works on a project that has a comp
// called "Comp 1" with those two layers at positions 24 and 39.

var comp = null;
for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it instanceof CompItem && it.name == "Comp 1") comp = it; }
if (!comp) throw new Error("Comp 1 not found");
var clouds = comp.layer("clouds"), moving = comp.layer("moving clouds");
if (clouds.index != 24 || moving.index != 39) throw new Error("layers are not where expected: " + clouds.index + ", " + moving.index);
var before = comp.numLayers;
clouds.locked = false; moving.locked = false;
var made = comp.layers.precompose([clouds.index, moving.index], "Clouds Comp", true);
// keep the two layers locked inside the new comp, as they were in Comp 1
for (var j = 1; j <= made.numLayers; j++) { made.layer(j).locked = true; }
print("Comp 1 layers:", before, "->", comp.numLayers);
for (var k = 1; k <= comp.numLayers; k++) { var L = comp.layer(k); if (L.source == made) print("new layer in Comp 1: #" + k, "[" + L.name + "]", "locked:", L.locked, "| above it:", comp.layer(k - 1).name, "| below it:", comp.layer(k + 1).name); }
print("new comp:", "[" + made.name + "]", made.width + "x" + made.height, made.duration + "s", made.frameRate + " fps");
for (var j = 1; j <= made.numLayers; j++) { var M = made.layer(j); print("  inside #" + j, "[" + M.name + "]", "opacity", M.property("ADBE Transform Group").property("ADBE Opacity").value, "pos keys", M.property("ADBE Transform Group").property("ADBE Position").numKeys, "masks", M.property("ADBE Mask Parade").numProperties, "locked", M.locked); }
print("project has unsaved changes:", app.project.dirty);
