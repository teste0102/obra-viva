import bpy, sys, math, os, random
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
FASE = int(a[0]); SAIDA = os.path.expanduser(a[1]); W, H, S = (int(a[2]), int(a[3]), int(a[4])) if len(a) >= 5 else (1664, 1248, 128)
OBJ = os.path.expanduser("~/ferramentas/skp/out/farmhouse3.obj")
ORDEM = [[], ["10_-_Foundation"], ["11_-_L1_Floor"], ["12_-_L1_Walls"], ["13_-_L2_Floor"], ["14_-_L2_Walls"], ["15_-_Roof"], ["Layer0", "Gutters"],
         ["21_-_Windows_in_3D", "20_-_Window", "Door_-_3D", "Door", "23_-_Shutters", "09_Finishes"]]
VIS = [p for f in ORDEM[:FASE + 1] for p in f]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="Y", up_axis="Z")


def mat(nome, cor, rug=0.6, metal=0.0, trans=0.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*cor, 1); p.inputs["Roughness"].default_value = rug
    p.inputs["Metallic"].default_value = metal; p.inputs["Transmission Weight"].default_value = trans
    return m


CONC = mat("conc", (0.46, 0.45, 0.43), 0.92); MAD = mat("mad", (0.58, 0.42, 0.26), 0.7); OSB = mat("osb", (0.64, 0.5, 0.33), 0.85)
PRIM = mat("prim", (0.52, 0.54, 0.57), 0.7); TELHA = mat("telha", (0.62, 0.64, 0.66), 0.33, metal=0.95); CALHA = mat("calha", (0.55, 0.55, 0.53), 0.45, metal=0.8)
VIDRO = mat("vidro", (0.9, 0.95, 1.0), 0.02, trans=1.0); VERDE = mat("verde", (0.035, 0.12, 0.06), 0.42); BRANCO = mat("branco", (0.86, 0.86, 0.83), 0.55)
PAREDE = OSB if FASE < 8 else PRIM
PADRAO = {"10_-_Foundation": CONC, "11_-_L1_Floor": MAD, "13_-_L2_Floor": MAD, "12_-_L1_Walls": PAREDE, "14_-_L2_Walls": PAREDE,
          "15_-_Roof": TELHA, "Layer0": MAD, "Gutters": CALHA, "21_-_Windows_in_3D": BRANCO, "20_-_Window": BRANCO,
          "Door_-_3D": MAD, "Door": MAD, "23_-_Shutters": VERDE, "09_Finishes": BRANCO}
for o in list(bpy.context.scene.objects):
    if o.type != "MESH":
        continue
    camada = o.name.split("@")[0].split(".")[0]
    if camada not in VIS:
        o.hide_render = True; o.hide_viewport = True; continue
    for sl in o.material_slots:
        n = sl.material.name.lower() if sl.material else ""
        sl.material = VIDRO if "glass" in n else PADRAO.get(camada, MAD)

# chao de terra com cascalho
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -0.9)); chao = bpy.context.active_object
mt = bpy.data.materials.new("terra"); mt.use_nodes = True; nt = mt.node_tree; pb = nt.nodes["Principled BSDF"]
ns = nt.nodes.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 18; ns.inputs["Detail"].default_value = 9
rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (0.22, 0.14, 0.08, 1); rp.color_ramp.elements[1].color = (0.46, 0.33, 0.21, 1)
nt.links.new(ns.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], pb.inputs["Base Color"]); pb.inputs["Roughness"].default_value = 1.0
bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.6
nt.links.new(ns.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], pb.inputs["Normal"])
chao.data.materials.append(mt)
CASC = mat("casc", (0.5, 0.5, 0.5), 0.95)
for (x, y, r) in [(-9, -15, 1.7), (5, -17, 1.5), (13, -13, 1.2)]:
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r, radius2=0.1, depth=r * 0.55, location=(x, y, -0.9 + r * 0.27))
    bpy.context.active_object.data.materials.append(CASC)

# carvalhos de volume bem ao fundo (anel de 75-95 m)
FOLHA = mat("folha", (0.05, 0.14, 0.03), 0.9)


def carvalho(x, y, esc, seed):
    random.seed(seed)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45 * esc, depth=5.5 * esc, location=(x, y, -0.9 + 2.7 * esc))
    bpy.context.active_object.data.materials.append(MAD)
    for k in range(36):
        ang = random.uniform(0, 6.283); d = (random.random() ** 0.6) * 6.2 * esc
        zz = -0.9 + (7.2 + random.uniform(0, 3.0) * (1 - d / (6.5 * esc)) + random.uniform(-0.4, 1.4)) * esc
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(1.3, 2.5) * esc,
                                              location=(x + d * math.cos(ang), y + d * math.sin(ang), zz))
        o = bpy.context.active_object; o.scale.z = 0.78; o.data.materials.append(FOLHA)


for k in range(11):
    ang = math.radians(k * 360 / 11 + 12); rr = 78 + 14 * ((k * 7) % 3) / 2
    carvalho(rr * math.cos(ang), rr * math.sin(ang) - 1, 2.4 + 0.2 * (k % 3), 20 + k)

# ceu e sol
w = bpy.data.worlds.new("Ceu"); bpy.context.scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new("ShaderNodeTexSky"); sky.sky_type = "NISHITA"; sky.sun_elevation = math.radians(52)
sky.sun_rotation = math.radians(-35); sky.sun_size = math.radians(0.6); sky.sun_intensity = 0.6
w.node_tree.links.new(sky.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
centro = Vector((0, -1, 5)); az = math.radians(-38); el = math.radians(5); R = 33
pos = centro + Vector((R * math.cos(el) * math.sin(az), -R * math.cos(el) * math.cos(az), R * math.sin(el)))
cam = bpy.data.cameras.new("Cam"); cam.lens = 35; co = bpy.data.objects.new("Cam", cam); bpy.context.collection.objects.link(co); co.location = pos
co.rotation_euler = (centro - pos).to_track_quat("-Z", "Y").to_euler(); bpy.context.scene.camera = co
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = S; sc.cycles.use_denoising = True
sc.render.resolution_x = W; sc.render.resolution_y = H
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = -1.3; sc.render.image_settings.file_format = "PNG"
pref = bpy.context.preferences.addons["cycles"].preferences
try:
    pref.compute_device_type = "OPTIX"; pref.refresh_devices()
    for d in pref.devices:
        d.use = (d.type == "OPTIX")
    sc.cycles.device = "GPU"
except Exception:
    sc.cycles.device = "CPU"
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
sc.render.filepath = SAIDA; bpy.ops.render.render(write_still=True); print("FASE_OK", FASE, SAIDA)
