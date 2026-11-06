"""Wan 2.2 Fun Control: ref_image = foto realista (Qwen), control_video = orbita do Blender (bordas Canny ou render cru)."""
import json, time, urllib.request, sys
sys.stdout.reconfigure(encoding="utf-8")
H = __import__("os").environ.get("COMFY_URL", "http://127.0.0.1:8188")
dan = json.load(open(__import__("os").path.expanduser("~/ferramentas/blender/danca8b_api.json"), encoding="utf8"))
REF, CTRL, MODO, TAG, SEED = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
TXT = ("A smooth aerial drone shot slowly circling around a white two-storey farmhouse with double-height wraparound porches, white columns and railings, dark green shutters, a silver standing seam metal roof and two red brick chimneys, "
       "standing on a mown green lawn with big live oak trees. The camera orbits steadily around the house while rising slightly. The house never changes shape: the porches, roof, chimneys, windows and shutters stay exactly the same. Warm late-afternoon sunlight, realistic, sharp, no people.")
NEG = "changing house shape, extra floors, missing porch, deformed roof, melting walls, warped columns, extra chimneys, people, text, watermark, blur, flicker"
a = {k: json.loads(json.dumps(dan[k])) for k in ["19", "20", "21", "22", "23", "24", "25", "26"]}
a["18"] = {"class_type": "VHS_LoadVideo", "inputs": dict(dan["18"]["inputs"], video=CTRL, force_rate=16, custom_width=832, custom_height=624, frame_load_cap=81, skip_first_frames=0)}
a["16"] = {"class_type": "LoadImage", "inputs": {"image": REF}}
a["27"] = {"class_type": "CLIPTextEncode", "inputs": {"text": TXT, "clip": ["19", 0]}}
a["28"] = {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["19", 0]}}
ctrl = ["18", 0]
if MODO == "canny":
    a["60"] = {"class_type": "Canny", "inputs": {"image": ["18", 0], "low_threshold": 0.12, "high_threshold": 0.35}}
    ctrl = ["60", 0]
a["30"] = {"class_type": "Wan22FunControlToVideo", "inputs": {"width": 832, "height": 624, "length": 81, "batch_size": 1, "positive": ["27", 0], "negative": ["28", 0], "vae": ["20", 0], "ref_image": ["16", 0], "control_video": ctrl}}
a["31"] = dict(dan["31"]); a["31"] = json.loads(json.dumps(dan["31"])); a["31"]["inputs"]["noise_seed"] = SEED
a["32"] = json.loads(json.dumps(dan["32"])); a["33"] = json.loads(json.dumps(dan["33"]))
a["55"] = {"class_type": "CreateVideo", "inputs": {"fps": 16, "images": ["33", 0]}}
a["56"] = {"class_type": "SaveVideo", "inputs": {"filename_prefix": "construcoes21/orbita_%s" % TAG, "format": "auto", "codec": "auto", "video": ["55", 0]}}
a["61"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "construcoes21/orbita_%s_controle" % TAG, "images": ["60", 0] if MODO == "canny" else ["18", 0]}}
# o 1o quadro do controle como imagem de conferencia (so a 1a imagem: ImageFromBatch)
a["61"]["inputs"]["images"] = ["62", 0]
a["62"] = {"class_type": "ImageFromBatch", "inputs": {"image": ctrl, "batch_index": 0, "length": 1}}
r = urllib.request.Request(H + "/prompt", data=json.dumps({"prompt": a, "client_id": "comfy-ui-web"}).encode(), headers={"Content-Type": "application/json"})
try: pid = json.load(urllib.request.urlopen(r, timeout=60))["prompt_id"]
except urllib.error.HTTPError as e: print("REJEITADO", e.read()[:900]); raise SystemExit(1)
print("na fila", TAG, pid, flush=True)
t0 = time.time()
while time.time() - t0 < 2400:
    time.sleep(15)
    try: h = json.load(urllib.request.urlopen(H + "/history/" + pid, timeout=30))
    except Exception: continue
    if pid in h:
        print("FIM", TAG, h[pid]["status"]["status_str"], round(time.time() - t0), "s", flush=True)
        if h[pid]["status"]["status_str"] != "success": print(json.dumps(h[pid]["status"])[:800])
        break
