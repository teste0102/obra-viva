"""Cena da Southern Farmhouse no Blender (headless). uso: blender -b --python cena.py -- <azimute_graus> <elev_graus> <raio_m> <saida.png> [largura altura amostras]"""
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]  # az0 az1 el0 el1 R frames W H amostras saida_dir [com_arvores]
AZ0, AZ1, EL0, EL1, R, NF, W, H, S, SAIDA = float(a[0]), float(a[1]), float(a[2]), float(a[3]), float(a[4]), int(a[5]), int(a[6]), int(a[7]), int(a[8]), os.path.expanduser(a[9])
ARV = (a[10] != "0") if len(a) > 10 else True
OBJ = os.path.expanduser("~/ferramentas/skp/out/farmhouse2.obj")
ESCONDER = ["10_Fixtures_(Arch)"]       # interior
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="Y", up_axis="Z")
for o in bpy.context.scene.objects:
    if any(o.name.startswith(n) for n in ESCONDER): o.hide_render = True; o.hide_viewport = True
# ---- materiais reais (substituem os marcadores do arquivo)
def novo_mat(nome, cor, rug=0.5, metal=0.0, trans=0.0, alpha=1.0, bump_tex=None):
    m = bpy.data.materials.new(nome); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*cor, 1); p.inputs["Roughness"].default_value = rug; p.inputs["Metallic"].default_value = metal
    p.inputs["Transmission Weight"].default_value = trans; p.inputs["Alpha"].default_value = alpha
    if alpha < 1: m.blend_method = "BLEND"
    return m
def tijolo(nome):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Color1"].default_value = (0.30, 0.07, 0.04, 1); br.inputs["Color2"].default_value = (0.22, 0.05, 0.03, 1); br.inputs["Mortar"].default_value = (0.62, 0.58, 0.52, 1)
    br.inputs["Scale"].default_value = 6.0; br.inputs["Mortar Size"].default_value = 0.012; br.offset = 0.5
    co = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(co.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"]); p.inputs["Roughness"].default_value = 0.88
    bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.5; nt.links.new(br.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], p.inputs["Normal"])
    return m
TINTA = novo_mat("Tinta_branca", (0.86, 0.86, 0.83), 0.55)
def bisel(m, raio):
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    bv = nt.nodes.new("ShaderNodeBevel"); bv.inputs["Radius"].default_value = raio; bv.samples = 8
    nt.links.new(bv.outputs["Normal"], p.inputs["Normal"])
bisel(TINTA, 0.010)

VERDE = novo_mat("Verde_veneziana", (0.035, 0.12, 0.06), 0.42)
bisel(VERDE, 0.006)
TELHA = novo_mat("Telha_prata", (0.62, 0.64, 0.66), 0.33, metal=0.95)
CALHA = novo_mat("Calha_prata", (0.62, 0.62, 0.60), 0.4, metal=0.9)
VIDRO = novo_mat("Vidro", (0.9, 0.95, 1.0), 0.02, trans=1.0)
MADEIRA = novo_mat("Madeira_deck", (0.42, 0.26, 0.14), 0.62)
TELA = novo_mat("Tela_varanda", (0.03, 0.03, 0.03), 0.8, alpha=0.35)
CONCR = novo_mat("Concreto", (0.55, 0.54, 0.52), 0.9)
TIJ = tijolo("Tijolo")
MAPA = [("clapboard", TINTA), ("louver", VERDE), ("metal_roofing", TELHA), ("metal_corrog", TELHA), ("old_silver", CALHA), ("glass", VIDRO), ("wood_floor", MADEIRA), ("black_dots", TELA),
        ("concrete", CONCR), ("brick", TIJ), ("herringbone", TIJ), ("course", TIJ), ("honeycomb", TIJ), ("beadboard", TINTA), ("_1", TINTA), ("_padrao", TINTA)]
for o in list(bpy.context.scene.objects):
    if o.type != "MESH": continue
    for i, slot in enumerate(o.material_slots):
        n = slot.material.name.lower() if slot.material else "_padrao"
        alvo = next((m for k, m in MAPA if k in n), TINTA)
        if n in ("_padrao", "_1") and o.name.startswith("10_-_Foundation"): alvo = TIJ
        if o.name.startswith("23_-_Shutters") and alvo is TINTA: alvo = VERDE
        if o.name.startswith("15_-_Roof") and alvo is TINTA: alvo = TELHA
        if o.name.startswith("Gutters"): alvo = CALHA
        slot.material = alvo
# ---- chao (gramado procedural)
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -0.9)); chao = bpy.context.active_object; chao.name = "Gramado"
mg = bpy.data.materials.new("Grama"); mg.use_nodes = True; nt = mg.node_tree; pb = nt.nodes["Principled BSDF"]
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 60; noise.inputs["Detail"].default_value = 8
rampa = nt.nodes.new("ShaderNodeValToRGB"); rampa.color_ramp.elements[0].color = (0.025, 0.09, 0.015, 1); rampa.color_ramp.elements[1].color = (0.10, 0.22, 0.04, 1)
nt.links.new(noise.outputs["Fac"], rampa.inputs["Fac"]); nt.links.new(rampa.outputs["Color"], pb.inputs["Base Color"]); pb.inputs["Roughness"].default_value = 0.95
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.4; nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], pb.inputs["Normal"])
chao.data.materials.append(mg)
# ---- ceu e sol
w = bpy.data.worlds.new("Ceu"); bpy.context.scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new("ShaderNodeTexSky"); sky.sky_type = "NISHITA"; sky.sun_elevation = math.radians(52); sky.sun_rotation = math.radians(-35); sky.sun_size = math.radians(0.6); sky.sun_intensity = 0.6; sky.altitude = 0
w.node_tree.links.new(sky.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"]); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

import random
# ---- carvalhos de volume (proxy) para dar paralaxe e referencia ao fundo
def carvalho(x, y, esc, seed):
    random.seed(seed)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45 * esc, depth=5.5 * esc, location=(x, y, -0.9 + 2.7 * esc)); tr = bpy.context.active_object
    tr.data.materials.append(MADEIRA)
    for k in range(36):
        ang = random.uniform(0, 6.283); d = (random.random() ** 0.6) * 6.2 * esc
        zz = -0.9 + (7.2 + random.uniform(0, 3.0) * (1 - d / (6.5 * esc)) + random.uniform(-0.4, 1.4)) * esc
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(1.3, 2.5) * esc, location=(x + d * math.cos(ang), y + d * math.sin(ang), zz))
        o = bpy.context.active_object; o.scale.z = 0.78; o.data.materials.append(FOLHA)
FOLHA = novo_mat("Folhagem", (0.05, 0.14, 0.03), 0.9)
nt2 = FOLHA.node_tree; ns = nt2.nodes.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 9; ns.inputs["Detail"].default_value = 10
bm2 = nt2.nodes.new("ShaderNodeBump"); bm2.inputs["Strength"].default_value = 1.0; bm2.inputs["Distance"].default_value = 0.4; nt2.links.new(ns.outputs["Fac"], bm2.inputs["Height"]); nt2.links.new(bm2.outputs["Normal"], nt2.nodes["Principled BSDF"].inputs["Normal"])
rp = nt2.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (0.02, 0.08, 0.015, 1); rp.color_ramp.elements[1].color = (0.12, 0.26, 0.05, 1); nt2.links.new(ns.outputs["Fac"], rp.inputs["Fac"]); nt2.links.new(rp.outputs["Color"], nt2.nodes["Principled BSDF"].inputs["Base Color"])
if ARV:
    import math as _m
    for k in range(11):
        ang = _m.radians(k * 360 / 11 + 12); rr = 78 + 14 * ((k * 7) % 3) / 2
        carvalho(rr * _m.cos(ang), rr * _m.sin(ang) - 1, 2.4 + 0.2 * (k % 3), 20 + k)
# ---- camera animada
centro = Vector((0.0, -1.0, 5.0))
cam = bpy.data.cameras.new("Cam"); cam.lens = 35; co = bpy.data.objects.new("Cam", cam); bpy.context.collection.objects.link(co); bpy.context.scene.camera = co
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = S; sc.cycles.use_denoising = True; sc.render.resolution_x = W; sc.render.resolution_y = H
sc.view_settings.exposure = -1.3; sc.render.image_settings.file_format = "PNG"; sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
pref = bpy.context.preferences.addons["cycles"].preferences
try:
    pref.compute_device_type = "OPTIX"; pref.refresh_devices()
    for d in pref.devices: d.use = (d.type == "OPTIX")
    sc.cycles.device = "GPU"; print("DISPOSITIVO: GPU OptiX")
except Exception as e: print("GPU indisponivel, usando CPU:", e); sc.cycles.device = "CPU"
os.makedirs(SAIDA, exist_ok=True)
for i in range(NF):
    t = i / max(NF - 1, 1); t = t * t * (3 - 2 * t)                  # partida e chegada suaves
    az = math.radians(AZ0 + (AZ1 - AZ0) * t); el = math.radians(EL0 + (EL1 - EL0) * t)
    pos = centro + Vector((R * math.cos(el) * math.sin(az), -R * math.cos(el) * math.cos(az), R * math.sin(el)))
    co.location = pos; co.rotation_euler = (centro - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(SAIDA, "f_%04d.png" % (i + 1)); bpy.ops.render.render(write_still=True)
    print("QUADRO", i + 1, "/", NF, flush=True)
print("ORBITA_OK", SAIDA)
