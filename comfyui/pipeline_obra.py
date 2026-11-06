"""Obra refeita com a geometria REAL do .skp (fases por camada), no mesmo angulo A do giro. Espera o giro (pipeline_giro2) terminar.
Etapas: render Blender por fase -> foto realista (Qwen+Qwendle, denoise 0,85) -> Wan primeiro/ultimo quadro (9 trechos) -> junta -> amplia 2x -> emenda com o giro."""
import os, sys, subprocess, time
H = os.path.expanduser("~/ferramentas/blender"); os.chdir(H)
OUT = "/opt/comfy/ComfyUI/output"; IN = "/opt/comfy/ComfyUI/input"
BL = os.path.expanduser("~/blender/blender-4.5.15-linux-x64/blender")
LOG = H + "/pipeline_obra.log"


def log(m):
    l = time.strftime("%d/%m %H:%M:%S") + "  " + m
    print(l, flush=True); open(LOG, "a").write(l + "\n")


def sh(cmd, timeout=3600, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=timeout, env=e)
    return r.stdout + r.stderr


def existe(p):
    return os.path.exists(p)


def parar(m):
    log("PARADO: " + m); sys.exit(1)


def probe(p):
    s = sh(f"ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height -of csv=p=0 {p}").strip().splitlines()
    return s[-1] if s else "?"


log("INICIO pipeline_obra: esperando o giro terminar")
while True:
    t = open(H + "/pipeline_giro2.log").read() if existe(H + "/pipeline_giro2.log") else ""
    if "PRONTO" in t:
        break
    if "PARADO" in t:
        parar("o giro parou; veja pipeline_giro2.log")
    if "INICIO" in t and not sh("pgrep -f pipeline_giro2.py").strip():
        parar("o processo do giro sumiu sem terminar")
    time.sleep(30)
log("giro pronto; comecando a obra")

BASE = ("Turn this 3D render into a real photograph of a house construction site. Keep exactly the same camera angle, composition, shapes and positions of every part shown, and add nothing else. "
        "Bare brown dirt ground with wheel tracks and a few gravel piles, no lawn. Big live oak trees in the background. Bright natural daylight, neutral realistic colors, sharp realistic detail, finished neat carpentry with straight edges, no people, no text. ")
P = [
    BASE + "The lot is empty: only dirt, gravel piles and the trees. There is no building at all.",
    BASE + "The only construction is a low concrete perimeter foundation wall faced with red brick and square red brick piers standing on the dirt, with a few wooden stakes.",
    BASE + "The only construction is the concrete and brick foundation with a raw wooden floor deck platform (plywood subfloor on joists) resting on it. No walls.",
    BASE + "The construction shows the foundation, the wooden floor deck and the first-floor walls of raw wood framing with OSB sheathing and empty window and door openings, and a brick chimney. No second floor and no roof.",
    BASE + "The construction shows the first-floor walls of raw wood and OSB, and above them a raw wooden second-floor deck platform. No second-floor walls and no roof.",
    BASE + "The construction shows both floors with raw wood and OSB walls and empty window openings, with a tall brick chimney, and no roof yet.",
    BASE + "The construction shows both floors with raw wood and OSB walls and the new silver standing seam metal roof with the two brick chimneys. No railings and no columns yet.",
    BASE + "The construction shows the walls, the silver metal roof, raw wooden porch columns, raw wooden porch decks and raw wooden railings with evenly spaced straight balusters, and gutters. Windows are still empty openings.",
    BASE + "The construction is nearly finished: gray primed fiber-cement lap siding on all walls, installed windows and doors, unpainted dark green shutters, a raw wood porch with straight evenly spaced railings, and the silver metal roof. Still a dirt site.",
]
ESC = "Small realistic construction workers, six feet tall, their heads reach only two thirds of the wall height, far from the camera. "
T = [
    ESC + "Time-lapse of a construction site. Workers pour concrete and lay red brick: the low perimeter foundation wall and the brick piers rise from the bare dirt. The camera is static and the trees do not move.",
    ESC + "Time-lapse. Workers lay wooden joists and a plywood subfloor deck on top of the foundation. Static camera.",
    ESC + "Time-lapse. Workers raise the first-floor wall framing with OSB sheathing, the window openings and the brick chimney. Static camera.",
    ESC + "Time-lapse. Workers build the raw wooden second-floor deck platform over the first-floor walls. Static camera.",
    ESC + "Time-lapse. Workers raise the second-floor walls of raw wood and OSB. Static camera.",
    ESC + "Time-lapse. Workers install the roof trusses and the silver standing seam metal roof, and the brick chimneys. Static camera.",
    ESC + "Time-lapse. Workers build the raw wooden porch columns, porch decks and straight evenly spaced railings, and hang the gutters. Static camera.",
    ESC + "Time-lapse. Workers install windows and doors, nail gray primed siding and hang the shutters. Static camera.",
    "Time-lapse. The house is painted white with green shutters, the site is cleaned and a green lawn is rolled out around it; only two small landscapers work far from the camera. Static camera, very slow and smooth.",
]
# 1) fases: render do Blender + foto realista
for i in range(9):
    if not existe(f"{IN}/obra2_F{i}.png"):
        log(f"F{i}: render do Blender (fase {i})")
        o = sh(f"{BL} -b --factory-startup --python cena_fases.py -- {i} out/obra2_F{i}.png 1664 1248 128 2>&1 | grep -E 'FASE_OK|Error|Traceback' | head -3; sudo -n -u comfy cp out/obra2_F{i}.png {IN}/obra2_F{i}.png")
        if "FASE_OK" not in o or not existe(f"{IN}/obra2_F{i}.png"):
            parar(f"F{i}: render falhou\n{o[-400:]}")
    foto = f"{OUT}/construcoes22/obra2_F{i}_v0_00001_.png"
    if not existe(foto):
        log(f"F{i}: foto realista (Qwen + Qwendle 0,7, denoise 0,85)")
        o = sh(f"python3 -u roda_foto_srv.py obra2_F{i}.png obra2_F{i} 3 'bigly_merge_1.safetensors:0.7'", env={"DENO": "0.85", "PROMPT": P[i]})
        if "success" not in o or not existe(foto):
            parar(f"F{i}: foto falhou\n{o[-500:]}")
log("9 fases fotografadas; a 10a (casa pronta) e a foto do inicio do giro")
FIM = "construcoes22/g2_S1_v0_00001_.png [output]"
# 2) trechos do Wan entre as fases
for i in range(9):
    vid = f"{OUT}/construcoes23/obra_seg_{i:02d}_00001_.mp4"
    if existe(vid):
        continue
    a = f"construcoes22/obra2_F{i}_v0_00001_.png [output]"
    b = FIM if i == 8 else f"construcoes22/obra2_F{i + 1}_v0_00001_.png [output]"
    log(f"trecho {i}: Wan primeiro/ultimo quadro (~5 min)")
    o = sh(f"python3 -u roda_flf_srv.py '{a}' '{b}' {i} '{T[i]}' {21 + i}")
    if "success" not in o or not existe(vid):
        parar(f"trecho {i}: Wan falhou\n{o[-600:]}")
    log(f"trecho {i}: OK [{probe(vid)}]")
# 3) junta os 9 trechos
V = [f"{OUT}/construcoes23/obra_seg_{i:02d}_00001_.mp4" for i in range(9)]
ins = " ".join(f"-i {v}" for v in V); lig = "".join(f"[{i}:v]" for i in range(9))
log("juntando os 9 trechos da obra")
sh(f"cd /tmp && sudo -n -u comfy ffmpeg -nostdin -v error -y {ins} -filter_complex \"{lig}concat=n=9:v=1[o]\" -map \"[o]\" -c:v libx264 -crf 14 -pix_fmt yuv420p {OUT}/construcoes23/obra2_832.mp4")
c = probe(f"{OUT}/construcoes23/obra2_832.mp4"); log(f"obra2 832: {c}")
if not c.startswith("832,624"):
    parar("juncao da obra falhou")
# 4) amplia 2x
log("ampliando a obra 2x (4x-UltraSharp, ~20 min)")
sh(f"cd /tmp && sudo -n -u comfy /opt/comfy/venv/bin/python /tmp/ampliar_video2.py {OUT}/construcoes23/obra2_832.mp4 {OUT}/construcoes23/obra2_2x.mp4 /opt/comfy/ComfyUI/models/upscale_models/4x-UltraSharp.pth 832 624 16", 5400)
c = probe(f"{OUT}/construcoes23/obra2_2x.mp4"); log(f"obra2 2x: {c}")
if not c.startswith("1664,1248"):
    parar("ampliacao da obra falhou")
# 5) emenda final: obra + giro (corte seco; o giro perde o 1o quadro, igual ao ultimo da obra)
log("emendando obra + giro")
sh(f"cd /tmp && sudo -n -u comfy ffmpeg -nostdin -v error -y -i {OUT}/construcoes23/obra2_2x.mp4 -i {OUT}/construcoes21/giro2_completo_2x.mp4 "
   f"-filter_complex \"[1:v]trim=start_frame=1,setpts=PTS-STARTPTS[g];[0:v][g]concat=n=2:v=1[o]\" -map \"[o]\" -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p -movflags +faststart {OUT}/construcoes23/obra_giro_final_2x.mp4", 3600)
c = probe(f"{OUT}/construcoes23/obra_giro_final_2x.mp4"); log(f"VIDEO FINAL: {c}")
sh(f"cd /tmp && sudo -n -u comfy ffmpeg -nostdin -v error -y -i {OUT}/construcoes23/obra_giro_final_2x.mp4 -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p -movflags +faststart {OUT}/construcoes23/obra_giro_final_2x_leve.mp4", 3600)
log("PRONTO: construcoes23/obra_giro_final_2x.mp4 e _leve.mp4 (no servidor)")
