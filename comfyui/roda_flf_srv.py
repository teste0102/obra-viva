"""Wan 2.2 primeiro-ultimo quadro (um trecho da obra). uso: roda_flf_srv.py <img0> <img1> <indice> <texto> <semente>"""
import json, sys, time, urllib.request, os
H = __import__("os").environ.get("COMFY_URL", "http://127.0.0.1:8188")
api = json.load(open(os.path.expanduser("~/ferramentas/blender/construcoes18_api.json"), encoding="utf8"))
neg = [v["inputs"]["text"] for v in api.values() if v["class_type"] == "CLIPTextEncode" and str(v["_meta"]["title"]).startswith("Negativo")][0]
IMG0, IMG1, IDX, TEXTO, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
a = {
    "1": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
    "2": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
    "3": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
    "4": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
    "5": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "strength_model": 1, "model": ["3", 0]}},
    "6": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors", "strength_model": 1, "model": ["4", 0]}},
    "7": {"class_type": "ModelSamplingSD3", "inputs": {"shift": 5, "model": ["5", 0]}},
    "8": {"class_type": "ModelSamplingSD3", "inputs": {"shift": 5, "model": ["6", 0]}},
    "9": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 0]}},
    "10": {"class_type": "CLIPTextEncode", "inputs": {"text": TEXTO, "clip": ["1", 0]}},
    "11": {"class_type": "LoadImage", "inputs": {"image": IMG0}},
    "12": {"class_type": "LoadImage", "inputs": {"image": IMG1}},
    "13": {"class_type": "WanFirstLastFrameToVideo", "inputs": {"width": 832, "height": 624, "length": 81, "batch_size": 1, "positive": ["10", 0], "negative": ["9", 0], "vae": ["2", 0], "start_image": ["11", 0], "end_image": ["12", 0]}},
    "14": {"class_type": "KSamplerAdvanced", "inputs": {"add_noise": "enable", "noise_seed": SEED, "steps": 4, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "start_at_step": 0, "end_at_step": 2, "return_with_leftover_noise": "enable", "model": ["7", 0], "positive": ["13", 0], "negative": ["13", 1], "latent_image": ["13", 2]}},
    "15": {"class_type": "KSamplerAdvanced", "inputs": {"add_noise": "disable", "noise_seed": 0, "steps": 4, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "start_at_step": 2, "end_at_step": 10000, "return_with_leftover_noise": "disable", "model": ["8", 0], "positive": ["13", 0], "negative": ["13", 1], "latent_image": ["14", 0]}},
    "16": {"class_type": "VAEDecode", "inputs": {"samples": ["15", 0], "vae": ["2", 0]}},
}
src = ["16", 0]
if IDX > 0:
    a["17"] = {"class_type": "ImageFromBatch", "inputs": {"image": ["16", 0], "batch_index": 1, "length": 80}}
    src = ["17", 0]
a["18"] = {"class_type": "CreateVideo", "inputs": {"fps": 16, "images": src}}
a["19"] = {"class_type": "SaveVideo", "inputs": {"filename_prefix": "construcoes23/obra_seg_%02d" % IDX, "format": "auto", "codec": "auto", "video": ["18", 0]}}
r = urllib.request.Request(H + "/prompt", data=json.dumps({"prompt": a, "client_id": "comfy-ui-web"}).encode(), headers={"Content-Type": "application/json"})
try:
    pid = json.load(urllib.request.urlopen(r, timeout=60))["prompt_id"]
except urllib.error.HTTPError as e:
    print("REJEITADO", e.read()[:600]); raise SystemExit(1)
t0 = time.time()
while time.time() - t0 < 2400:
    time.sleep(15)
    try:
        h = json.load(urllib.request.urlopen(H + "/history/" + pid, timeout=30))
    except Exception:
        continue
    if pid in h:
        print("FIM", IDX, h[pid]["status"]["status_str"], round(time.time() - t0), "s"); break
