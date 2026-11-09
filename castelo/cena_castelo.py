"""Castelo de pedra, camera fixa, fases da obra (muralhas e partes altas primeiro).
uso: blender -b --python cena_castelo.py -- <fase> <saida.png> <W> <H> <amostras>
env: TEX (castle_brick_07 | large_sandstone_blocks_01 | stone_brick_wall_001), ESC (metros por repeticao da textura)
Fases: 0 terreno | 1 fundacao de pedra (plinto) | 2 muralha 3 m | 3 muralha 6 m | 4 muralha 9 m com passadico |
       5 ameias | 6 portal do portao (arco) | 7 bases das torres de canto | 8 torre de menagem (base)"""
import bpy, sys, math, os, random
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
FASE = int(a[0]); SAIDA = os.path.expanduser(a[1]); W, H, S = int(a[2]), int(a[3]), int(a[4])
TEX = os.environ.get("TEX", "castle_brick_07"); ESC = float(os.environ.get("ESC", "3.0"))
TD = os.path.expanduser("~/ferramentas/castelo/tex/")
bpy.ops.wm.read_factory_settings(use_empty=True)
Z0 = 0.0
HX, HY, T = 17.0, 13.0, 2.4          # meia-largura, meia-profundidade, espessura da muralha


def mat_pedra(nome, tint=(1, 1, 1)):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / ESC, 1 / ESC, 1 / ESC)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    def img(arq, cs):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(TD + TEX + "_" + arq + ".jpg"); n.image.colorspace_settings.name = cs
        n.projection = "BOX"; n.projection_blend = 0.1; nt.links.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    d = img("Diffuse", "sRGB"); r = img("Rough", "Non-Color"); nn = img("nor_gl", "Non-Color")
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.6
    nt.links.new(nn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(d.outputs["Color"], p.inputs["Base Color"]); nt.links.new(r.outputs["Color"], p.inputs["Roughness"])
    return m


def mat(nome, cor, rug=0.6):
    m = bpy.data.materials.new(nome); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*cor, 1); p.inputs["Roughness"].default_value = rug; return m


PEDRA = mat_pedra("pedra"); MAD = mat("mad", (0.58, 0.42, 0.26), 0.75); BLOCO = mat_pedra("bloco")


def caixa(x0, x1, y0, y1, z0, z1, m=PEDRA, nome="c"):
    bpy.ops.mesh.primitive_cube_add(location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); o = bpy.context.active_object
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2); bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m); o.name = nome
    return o


def muralha(alt, plinto=False):
    """anel retangular com abertura do portao na frente (y negativo)"""
    ex = HX + (0.5 if plinto else 0); ey = HY + (0.5 if plinto else 0); t = T + (1.0 if plinto else 0); z0 = Z0 - (0.6 if plinto else 0)
    gw = 2.6 + (0.5 if plinto else 0)
    partes = [caixa(-ex - t / 2, ex + t / 2, ey - t / 2, ey + t / 2, z0, alt, nome="norte"),
              caixa(-ex - t / 2, -ex + t / 2, -ey, ey, z0, alt, nome="oeste"),
              caixa(ex - t / 2, ex + t / 2, -ey, ey, z0, alt, nome="leste"),
              caixa(-ex - t / 2, -gw, -ey - t / 2, -ey + t / 2, z0, alt, nome="sul_a"),
              caixa(gw, ex + t / 2, -ey - t / 2, -ey + t / 2, z0, alt, nome="sul_b")]
    return partes


# ---------- construcao por fase
ALT = {2: 3.0, 3: 6.0, 4: 9.0, 5: 9.0, 6: 9.0, 7: 9.0, 8: 9.0}
if FASE == 1:
    muralha(Z0 + 0.5, plinto=True)
elif FASE >= 2:
    muralha(ALT[FASE])
    if FASE >= 4:   # passadico: laje interna na altura 9 por dentro da muralha, mais parapeito interno baixo nao (ameias vem na fase 5)
        pass
if FASE >= 5:       # ameias: merlons de 1,5 m, vao de 1,0 m, no topo da muralha (lado de fora)
    zt = 9.0
    def fiada(x0, x1, y, eixo):
        n = int((x1 - x0) // 2.5)
        for i in range(n):
            s = x0 + i * 2.5 + 0.0
            if eixo == "x" and y < -HY and s + 1.5 > -2.7 and s < 2.7:
                continue
            if eixo == "x":
                caixa(s, s + 1.5, y - 0.6, y + 0.6, zt, zt + 1.5, nome="ameia")
            else:
                caixa(y - 0.6, y + 0.6, s, s + 1.5, zt, zt + 1.5, nome="ameia")
    for ys in (HY, -HY):
        fiada(-HX - 1.0, HX + 1.0, ys + (T / 2 - 0.6) * (1 if ys > 0 else -1), "x")
    for xs in (HX, -HX):
        fiada(-HY + 1.0, HY - 1.0, xs + (T / 2 - 0.6) * (1 if xs > 0 else -1), "y")
if FASE >= 6:       # portao: bloco de pedra sobre a abertura, com arco redondo recortado, aduelas salientes e portas de carvalho
    yc = -HY; ty = T + 0.2
    blk = caixa(-2.6, 2.6, yc - ty / 2, yc + ty / 2, Z0, 9.0, nome="portal")
    # recorte: retangulo ate 3,6 m + meio cilindro de raio 2,0 (arco)
    cut1 = caixa(-2.0, 2.0, yc - 3, yc + 3, Z0 - 0.5, 3.6, nome="cut1")
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2.0, depth=6, location=(0, yc, 3.6), rotation=(math.pi / 2, 0, 0)); cut2 = bpy.context.active_object
    for c in (cut1, cut2):
        mo = blk.modifiers.new("b", "BOOLEAN"); mo.operation = "DIFFERENCE"; mo.object = c
        bpy.context.view_layer.objects.active = blk; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(c)
    # anel de aduelas salientes (faixa em volta do arco)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2.45, depth=ty + 0.5, location=(0, yc, 3.6), rotation=(math.pi / 2, 0, 0)); an = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2.0, depth=ty + 1, location=(0, yc, 3.6), rotation=(math.pi / 2, 0, 0)); an2 = bpy.context.active_object
    cx = caixa(-2.0, 2.0, yc - 3, yc + 3, Z0 - 0.5, 3.6, nome="cx")
    for c in (an2, cx):
        mo = an.modifiers.new("b", "BOOLEAN"); mo.operation = "DIFFERENCE"; mo.object = c
        bpy.context.view_layer.objects.active = an; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(c)
    an.data.materials.append(PEDRA)
    # ameias sobre o portal
    for i in range(2):
        pass
    # portas de carvalho com tiras de ferro, meio abertas
    FERRO = mat("ferro", (0.05, 0.05, 0.06), 0.5)
    for lado in (-1, 1):
        xa, xb = (0.05, 1.95) if lado > 0 else (-1.95, -0.05)
        caixa(xa, xb, yc + 0.1, yc + 0.35, Z0, 3.6, MAD, "porta")
        for zz in (0.8, 1.8, 2.8):
            caixa(xa, xb, yc - 0.02, yc + 0.1, Z0 + zz, Z0 + zz + 0.14, FERRO, "ferro")
if FASE >= 6:
    zt = 9.0
    for i in range(4):
        caixa(-2.6 + i * 1.4 + 0.0, -2.6 + i * 1.4 + 0.9, yc - 0.6, yc + 0.6, zt, zt + 1.5, nome="ameia_portal")
if FASE >= 7:       # bases das torres de canto (cilindros de pedra, so ate a altura da muralha + 1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=4.0, depth=11.0, location=(sx * HX, sy * HY, Z0 + 5.5))
            o = bpy.context.active_object; o.data.materials.append(PEDRA); o.name = "torre"
if FASE >= 8:       # base da torre de menagem no centro
    caixa(-5, 5, -4, 4, Z0, 7.0, nome="menagem")

# ---------- andaimes de madeira (fases 2-4) pelo lado de fora da muralha sul e leste
if 2 <= FASE <= 4:
    h = ALT[FASE] + 1.5
    for (x0, y0, x1, y1) in [(-HX, -HY - T / 2 - 1.2, HX, -HY - T / 2 - 1.2), (HX + T / 2 + 1.2, -HY, HX + T / 2 + 1.2, HY)]:
        n = int(max(abs(x1 - x0), abs(y1 - y0)) // 3)
        for i in range(n + 1):
            f = i / max(n, 1); px = x0 + (x1 - x0) * f; py = y0 + (y1 - y0) * f
            caixa(px - 0.07, px + 0.07, py - 0.07, py + 0.07, Z0, h, MAD, "poste")
        for zz in range(2, int(h), 3):
            caixa(min(x0, x1) - 0.07, max(x0, x1) + 0.07 if x0 != x1 else x0 + 0.07, min(y0, y1) - 0.07 if y0 != y1 else y0 - 0.07,
                  max(y0, y1) + 0.07 if y0 != y1 else y0 + 0.07, Z0 + zz, Z0 + zz + 0.12, MAD, "prancha")

# ---------- pilhas de blocos de pedra e tabuas, terra, operarios
random.seed(7)
for (cx, cy) in [(-26, -22), (8, -26), (24, -20), (-30, 6)]:
    for k in range(14):
        caixa(cx + random.uniform(-2.2, 2.2), cx + random.uniform(-2.2, 2.2) + 1.2, cy + random.uniform(-1.5, 1.5), cy + random.uniform(-1.5, 1.5) + 0.8,
              Z0 + (k // 5) * 0.55, Z0 + (k // 5) * 0.55 + 0.55, BLOCO, "bloco")
bpy.ops.mesh.primitive_plane_add(size=800, location=(0, 0, Z0)); chao = bpy.context.active_object
mt = bpy.data.materials.new("terra"); mt.use_nodes = True; nt = mt.node_tree; pb = nt.nodes["Principled BSDF"]
ns = nt.nodes.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 18; ns.inputs["Detail"].default_value = 9
rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (0.22, 0.14, 0.08, 1); rp.color_ramp.elements[1].color = (0.46, 0.33, 0.21, 1)
nt.links.new(ns.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], pb.inputs["Base Color"]); pb.inputs["Roughness"].default_value = 1.0
chao.data.materials.append(mt)
COLETE = mat("colete", (0.9, 0.35, 0.02), 0.6); CALCA = mat("calca", (0.12, 0.14, 0.2), 0.8); PELE = mat("pele", (0.55, 0.38, 0.28), 0.7)
if FASE >= 1:
    for (px, py) in [(-6, -22), (7, -21), (-20, -15), (21, -10)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.85, location=(px, py, Z0 + 0.425)); bpy.context.active_object.data.materials.append(CALCA)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.21, depth=0.55, location=(px, py, Z0 + 1.12)); bpy.context.active_object.data.materials.append(COLETE)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.115, location=(px, py, Z0 + 1.63)); bpy.context.active_object.data.materials.append(PELE)

FOLHA = mat("folha", (0.05, 0.14, 0.03), 0.9)
def carvalho(x, y, esc, seed):
    random.seed(seed)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45 * esc, depth=5.5 * esc, location=(x, y, Z0 + 2.7 * esc)); bpy.context.active_object.data.materials.append(MAD)
    for k in range(36):
        ang = random.uniform(0, 6.283); d = (random.random() ** 0.6) * 6.2 * esc
        zz = Z0 + (7.2 + random.uniform(0, 3.0) * (1 - d / (6.5 * esc)) + random.uniform(-0.4, 1.4)) * esc
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(1.3, 2.5) * esc, location=(x + d * math.cos(ang), y + d * math.sin(ang), zz))
        o = bpy.context.active_object; o.scale.z = 0.78; o.data.materials.append(FOLHA)
for k in range(16):
    ang = math.radians(k * 360 / 16 + 12); rr = 105 + 16 * ((k * 7) % 3) / 2
    carvalho(rr * math.cos(ang), rr * math.sin(ang) - 1, 2.4 + 0.2 * (k % 3), 20 + k)

# ceu, sol, camera
w = bpy.data.worlds.new("Ceu"); bpy.context.scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new("ShaderNodeTexSky"); sky.sky_type = "NISHITA"; sky.sun_elevation = math.radians(52)
sky.sun_rotation = math.radians(-35); sky.sun_size = math.radians(0.6); sky.sun_intensity = 0.6
w.node_tree.links.new(sky.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
centro = Vector((0, 0, 4.5)); az = math.radians(-38); el = math.radians(9); R = 58
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
