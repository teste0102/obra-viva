
import os, sys, subprocess, time
H = os.path.expanduser("~/ferramentas/blender"); os.chdir(H)
OUT = "/opt/comfy/ComfyUI/output"; IN = "/opt/comfy/ComfyUI/input"
BL = os.path.expanduser("~/blender/blender-4.5.15-linux-x64/blender")
LOG = H + "/pipeline_giro2.log"
def log(m):
    l = time.strftime("%d/%m %H:%M:%S") + "  " + m; print(l, flush=True); open(LOG, "a").write(l + "\n")
def sh(cmd, timeout=3600, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=timeout, env=e); return r.stdout + r.stderr
def existe(p): return os.path.exists(p)
def parar(m): log("PARADO: " + m); sys.exit(1)
def probe(p):
    s = sh(f"ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height -of csv=p=0 {p}").strip().splitlines(); return s[-1] if s else "?"
SEG = [("S1", -38, 5, "orbita_A4_ctrl.mp4", 11), ("S2", 32, 7, "orbita_S2_ctrl.mp4", 12), ("S3", 102, 8, "orbita_S3_ctrl.mp4", 13)]
log("INICIO pipeline_giro2 (denoise 0,85, foto nova por trecho)")
for n, az, el, ctrl, sd in SEG:
    if not existe(f"{IN}/{ctrl}"): parar(f"guia {ctrl} nao existe no ComfyUI input")
    f0 = f"giro2_{n}_f0.png"
    if not existe(f"{IN}/{f0}"):
        log(f"{n}: render hi-res do Blender no inicio do trecho (az {az}, elev {el})")
        o = sh(f"{BL} -b --factory-startup --python cena_orbita.py -- {az} {az} {el} {el} 33 1 1664 1248 128 out/g2f0_{n} 2>&1 | grep -E 'ORBITA_OK|Error|Traceback' | head -3; sudo -n -u comfy cp out/g2f0_{n}/f_0001.png {IN}/{f0}")
        if "ORBITA_OK" not in o or not existe(f"{IN}/{f0}"): parar(f"{n}: render hi-res falhou\n{o[-400:]}")
    foto = f"{OUT}/construcoes22/g2_{n}_v0_00001_.png"
    if not existe(foto):
        log(f"{n}: foto realista (Qwen + Qwendle 0,7, denoise 0,85)")
        o = sh(f"python3 -u roda_foto_srv.py {f0} g2_{n} 3 'bigly_merge_1.safetensors:0.7'", env={"DENO": "0.85"})
        if "success" not in o or not existe(foto): parar(f"{n}: foto falhou\n{o[-500:]}")
    vid = f"{OUT}/construcoes21/orbita_giro2_{n}_00001_.mp4"
    if not existe(vid):
        log(f"{n}: Wan Fun Control (~5 min)")
        o = sh(f"python3 -u roda_fun_srv.py 'construcoes22/g2_{n}_v0_00001_.png [output]' {ctrl} cru giro2_{n} {sd}")
        if "success" not in o or not existe(vid): parar(f"{n}: Wan falhou\n{o[-600:]}")
    log(f"{n}: OK [{probe(vid)}]")
V = lambda n: f"{OUT}/construcoes21/orbita_giro2_{n}_00001_.mp4"
log("juntando os 3 trechos com fusao de 0,25 s nas emendas (mesma pose de camera)")
d = 0.25; seg = 81 / 16
o1 = seg - d; o2 = (seg * 2 - d) - d
sh(f"cd /tmp && sudo -n -u comfy ffmpeg -nostdin -v error -y -i {V('S1')} -i {V('S2')} -i {V('S3')} -filter_complex \"[0:v][1:v]xfade=transition=fade:duration={d}:offset={o1:.4f}[a];[a][2:v]xfade=transition=fade:duration={d}:offset={o2:.4f}[o]\" -map \"[o]\" -c:v libx264 -crf 14 -pix_fmt yuv420p {OUT}/construcoes21/giro2_completo_832.mp4")
c = probe(f"{OUT}/construcoes21/giro2_completo_832.mp4"); log(f"giro2 832: {c}")
if not c.startswith("832,624"): parar("juncao falhou")
log("ampliando 2x (4x-UltraSharp, ~7 min)")
sh(f"cd /tmp && sudo -n -u comfy /opt/comfy/venv/bin/python /tmp/ampliar_video2.py {OUT}/construcoes21/giro2_completo_832.mp4 {OUT}/construcoes21/giro2_completo_2x.mp4 /opt/comfy/ComfyUI/models/upscale_models/4x-UltraSharp.pth 832 624 16", 2400)
c = probe(f"{OUT}/construcoes21/giro2_completo_2x.mp4"); log(f"giro2 2x: {c}")
sh(f"cd /tmp && sudo -n -u comfy ffmpeg -nostdin -v error -y -i {OUT}/construcoes21/giro2_completo_2x.mp4 -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p -movflags +faststart {OUT}/construcoes21/giro2_completo_2x_leve.mp4")
log("PRONTO: construcoes21/giro2_completo_2x.mp4 e _leve.mp4 (no servidor)")
