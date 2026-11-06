"""Quadro do Blender -> foto realista com LoRAs de realismo opcionais. uso: roda_foto_lora.py <img> <tag> <seed> <nome|none:forca[,nome:forca]>..."""
import json, time, urllib.request, sys
sys.stdout.reconfigure(encoding="utf-8")
H = __import__("os").environ.get("COMFY_URL", "http://127.0.0.1:8188")
api = json.load(open(__import__("os").path.expanduser("~/ferramentas/blender/construcoes18_api.json"), encoding="utf8"))
IMG, TAG, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3]); VARS = sys.argv[4:]
P = ("Turn this 3D render into a real photograph taken with a professional camera, not a render and not a drawing. Keep exactly the same camera angle, composition, the same house with its two-storey wraparound porches, every window, door and shutter, the same roof and chimneys and the same tree positions. "
     "Real materials with fine detail: white painted wooden clapboard siding with visible boards and shadow lines, dark green louvered shutters with slats, white turned columns and white balusters, weathered wooden deck boards, a silver standing seam metal roof with visible seams and reflections, red brick chimneys and foundation piers with individual bricks and mortar. "
     "Big live oak trees with detailed leaves, a real mown lawn with natural grass texture. Bright natural daylight, soft realistic shadows, neutral colors, photographic depth of field, high detail, no people, no text.")
fila = []
for i, v in enumerate(VARS):
    a = {k: json.loads(json.dumps(api[k])) for k in ["1", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28"]}
    a["1"]["inputs"]["image"] = IMG; a["22"]["inputs"]["prompt"] = (__import__("os").environ.get("PROMPT") or P); a["27"]["inputs"]["seed"] = SEED; a["27"]["inputs"]["denoise"] = float(__import__("os").environ.get("DENO", "1"))
    ult = ["18", 0]; rot = []
    if v != "none":
        for j, item in enumerate(v.split(",")):
            nome, forca = item.rsplit(":", 1)
            a["4%d" % j] = {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": nome, "strength_model": float(forca), "model": ult}}
            ult = ["4%d" % j, 0]; rot.append(nome.split(".")[0][:10])
    a["19"]["inputs"]["model"] = ult
    a["99"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "construcoes22/%s_v%d" % (TAG, i), "images": ["28", 0]}}
    r = urllib.request.Request(H + "/prompt", data=json.dumps({"prompt": a, "client_id": "comfy-ui-web"}).encode(), headers={"Content-Type": "application/json"})
    try: pid = json.load(urllib.request.urlopen(r, timeout=60))["prompt_id"]
    except urllib.error.HTTPError as e: print("REJEITADO", v, e.read()[:700]); raise SystemExit(1)
    fila.append((i, v, pid)); print("na fila", i, v, flush=True)
t0 = time.time(); pend = {p: (i, v) for i, v, p in fila}
while pend and time.time() - t0 < 1200:
    time.sleep(8)
    for pid in list(pend):
        try: h = json.load(urllib.request.urlopen(H + "/history/" + pid, timeout=30))
        except Exception: continue
        if pid in h: print("FIM", pend[pid], h[pid]["status"]["status_str"], round(time.time() - t0), "s", flush=True); del pend[pid]
