import bpy, sys, math, os
from mathutils import Vector
OBJ = os.path.expanduser("~/ferramentas/skp/out/farmhouse3.obj"); SAIDA = os.path.expanduser("~/ferramentas/blender/out/camadas")
os.makedirs(SAIDA, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="Y", up_axis="Z")
mat = bpy.data.materials.new("cinza"); mat.use_nodes = True; mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.72, 0.68, 1)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in objs:
    o.data.materials.clear(); o.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -0.9)); ch = bpy.context.active_object; ch.data.materials.append(mat)
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.85, 0.95, 1)
bpy.ops.object.light_add(type="SUN", location=(10, -10, 20)); sun = bpy.context.active_object; sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(30))
centro = Vector((0, -1, 5)); az = math.radians(-38); el = math.radians(5); R = 33
pos = centro + Vector((R * math.cos(el) * math.sin(az), -R * math.cos(el) * math.cos(az), R * math.sin(el)))
cam = bpy.data.cameras.new("c"); cam.lens = 35; co = bpy.data.objects.new("c", cam); bpy.context.collection.objects.link(co); co.location = pos
co.rotation_euler = (centro - pos).to_track_quat("-Z", "Y").to_euler(); bpy.context.scene.camera = co
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 12; sc.cycles.use_denoising = False
sc.render.resolution_x = 640; sc.render.resolution_y = 480
nomes = sorted({o.name.split("@")[0].split(".")[0] for o in objs})
print("CAMADAS:", nomes)
for nm in nomes:
    for o in objs: o.hide_render = not o.name.startswith(nm)
    ch.hide_render = False
    sc.render.filepath = os.path.join(SAIDA, nm.replace("(", "").replace(")", "") + ".png"); bpy.ops.render.render(write_still=True); print("FEITO", nm, flush=True)
