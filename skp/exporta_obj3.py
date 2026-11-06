"""Farmhouse.skp -> OBJ+MTL (metros, Z para cima), um objeto por camada (tag), pulando camadas escondidas. uso: python exporta_obj2.py <saida> [camadas_extras_a_esconder separadas por |]"""
import sys, os, zipfile, collections, numpy as np
from carrega import carregar
from skppy.utils import transform_to_matrix4x4
IN2M = 0.0254
saida = sys.argv[1]; extras = [x for x in (sys.argv[2].split("|") if len(sys.argv) > 2 else []) if x]
ESCONDER = {"00 Ground", "91 - 1st Floor Plan Cut", "92 - 2nd Floor Plan Cut", "92 - Work Ceiling Cut", "93 - Work Trans Sctn", "94 - Work Long Sctn", "90 - Foundation Cut",
            "Door - Plan", "Door - Dash", "Door - Elev Only", "22 - Windows in Plan", "People", "Furniture", "Electrical"} | set(extras)
m = carregar()
lay = {l.id: l.name for l in (m.layers.values() if isinstance(m.layers, dict) else m.layers)}
defs = m.definitions if isinstance(m.definitions, dict) else {d.id: d for d in m.definitions}
mats = {mm.id: mm for mm in (m.materials.values() if isinstance(m.materials, dict) else m.materials)}
mat4 = lambda t: np.array(transform_to_matrix4x4(t), float)
V, VT, VN = [], [], []
OBJ = collections.defaultdict(lambda: collections.defaultdict(list))   # camada -> material -> [faces]
cont = collections.Counter(); pulados = collections.Counter(); caixa = [np.full(3, 1e18), np.full(3, -1e18)]
def faixa(z):
    return "FD" if z < -0.05 else "L1" if z < 3.3 else "L2" if z < 6.5 else "RF"
def emite(mesh, M, camada0, mat_inst):
    R = M[:3, :3]; espelhado = np.linalg.det(R) < 0
    for f in mesh.faces:
        pos = np.array(f.vertex_positions, float)
        w = (M @ np.c_[pos, np.ones(len(pos))].T).T[:, :3] * IN2M
        uvs = list(f.vertex_uvs) if f.vertex_uvs is not None else None
        if espelhado:
            w = w[::-1]
            if uvs is not None: uvs = uvs[::-1]
        caixa[0] = np.minimum(caixa[0], w.min(0)); caixa[1] = np.maximum(caixa[1], w.max(0))
        n = np.zeros(3)
        for k in range(len(w)): n += np.cross(w[k], w[(k + 1) % len(w)])      # Newell: normal pela geometria final
        ln = np.linalg.norm(n); n = n / ln if ln > 1e-12 else np.array([0, 0, 1.0])
        i0 = len(V) + 1; V.extend(w.tolist()); VN.append(n.tolist()); ni = len(VN)
        if uvs is not None: VT.extend(uvs)
        ti0 = len(VT) - len(w) + 1
        mn = f.material_name or mat_inst or "_padrao"
        camada = camada0 + "@" + faixa(float(w[:, 2].mean()))
        OBJ[camada][mn].append([(i0 + k, (ti0 + k) if uvs is not None else None, ni) for k in range(len(w))]); cont[camada] += 1
def anda(ents, nome, M, camada, inh):
    mesh = ents.prepare_mesh(nome, mats, inh)
    if mesh is not None and mesh.faces: emite(mesh, M, camada, mats[inh].name if inh in mats else None)
    for g in list(ents.groups) + list(ents.component_instances):
        cam = lay.get(g.layer_id) if g.layer_id is not None else camada
        if cam in ESCONDER: pulados[cam] += 1; continue
        d = defs.get(g.definition_id)
        if d is None: continue
        anda(d.entities, d.name or g.name or "def", M @ mat4(g.transform), cam or camada, g.material_id or inh)
anda(m.entities, "raiz", np.eye(4), "Layer0", None)
print("CAMADAS EXPORTADAS (faces):", dict(cont.most_common()))
print("SUBARVORES PULADAS:", dict(pulados))
print("FACES:", sum(cont.values()), "| vertices:", len(V))
print("CAIXA (m):", np.round(caixa[0], 2).tolist(), np.round(caixa[1], 2).tolist(), "| tamanho:", np.round(caixa[1] - caixa[0], 2).tolist())
os.makedirs("out", exist_ok=True); tex = {}
z = zipfile.ZipFile("Farmhouse.skp")
for i in z.infolist():
    p = i.filename
    if p.startswith("materials/") and p.lower().endswith((".png", ".jpg", ".jpeg")):
        pasta = p.split("/")[1]; dest = "out/tex/%s_%s" % (pasta.replace(" ", "_").replace("[", "").replace("]", ""), os.path.basename(p).replace(" ", "_"))
        os.makedirs("out/tex", exist_ok=True); open(dest, "wb").write(z.read(p)); tex.setdefault(pasta, dest)
mn_all = {mm.name: mm for mm in mats.values()}
usados = sorted({mn for c in OBJ.values() for mn in c})
with open(saida + ".mtl", "w") as f:
    for nome in usados:
        mm = mn_all.get(nome); c = getattr(mm, "color", None)
        kd = (c.r / 255, c.g / 255, c.b / 255) if c is not None and hasattr(c, "r") else (0.8, 0.8, 0.8)
        f.write("newmtl %s\nKd %.4f %.4f %.4f\nd %.3f\n" % (nome.replace(" ", "_"), *kd, getattr(mm, "alpha", 1.0) if mm else 1.0))
        t = tex.get(nome)
        if t: f.write("map_Kd %s\n" % os.path.relpath(t, os.path.dirname(saida)).replace("\\", "/"))
        f.write("\n")
with open(saida + ".obj", "w") as f:
    f.write("mtllib %s.mtl\n" % os.path.basename(saida))
    for v in V: f.write("v %.5f %.5f %.5f\n" % tuple(v))
    for t in VT: f.write("vt %.5f %.5f\n" % tuple(t))
    for n in VN: f.write("vn %.4f %.4f %.4f\n" % tuple(n))
    for camada, porMat in OBJ.items():
        f.write("o %s\n" % camada.replace(" ", "_"))
        for nome, loops in porMat.items():
            f.write("usemtl %s\n" % nome.replace(" ", "_"))
            for lp in loops: f.write("f " + " ".join(("%d/%s/%d" % (a, b, c)) if b else ("%d//%d" % (a, c)) for a, b, c in lp) + "\n")
print("OBJ:", saida + ".obj", round(os.path.getsize(saida + ".obj") / 1e6, 1), "MB | materiais:", len(usados), "| texturas:", len(tex))
