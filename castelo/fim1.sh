#!/bin/bash
cd ~/ferramentas/castelo
O=/opt/comfy/ComfyUI/output/castelo
rm -f lista.txt; for f in c_seg_01_00001_ c_seg_02_00002_ c_seg_03_00001_ c_seg_04_00001_ c_seg_05_00001_; do echo "file $O/$f.mp4" >> lista.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i lista.txt -c:v libx264 -crf 12 -pix_fmt yuv420p out/castelo1_832.mp4 && echo JUNTO
sudo -n -u comfy /opt/comfy/venv/bin/python ~/ferramentas/castelo/ampliar.py ~/ferramentas/castelo/out/castelo1_832.mp4 $O/castelo1_2x.mp4 /opt/comfy/ComfyUI/models/upscale_models/4x-UltraSharp.pth 832 624 16 2>&1 | tail -3
ffmpeg -y -loglevel error -i $O/castelo1_2x.mp4 -c:v libx264 -crf 24 -pix_fmt yuv420p out/castelo1_leve.mp4 && sudo -n -u comfy cp out/castelo1_leve.mp4 $O/castelo1_leve.mp4
echo FIM1_PRONTO; ls -la $O/castelo1*
