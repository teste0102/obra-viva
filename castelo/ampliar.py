"""uso: ampliar.py entrada.mp4 saida.mp4 modelo.pth W H fps  (4x-UltraSharp, reduz para 2x)"""
import sys, subprocess, numpy as np, torch, spandrel, cv2
ent, sai, mod, W, H, fps = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
m = spandrel.ModelLoader().load_from_file(mod).cuda().eval().half()
rd = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", ent, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
wr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W*2}x{H*2}", "-r", fps, "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", sai], stdin=subprocess.PIPE)
n = 0
while True:
    b = rd.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    t = torch.from_numpy(f).permute(2, 0, 1)[None].cuda().half() / 255
    with torch.no_grad(): o = m(t)
    o = (o[0].permute(1, 2, 0).float().clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
    o = cv2.resize(o, (W * 2, H * 2), interpolation=cv2.INTER_AREA)
    wr.stdin.write(o.tobytes()); n += 1
wr.stdin.close(); wr.wait(); print("AMPLIADO", n)
