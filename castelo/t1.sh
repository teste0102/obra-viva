#!/bin/bash
cd ~/ferramentas/castelo
BL=~/blender/blender-4.5.15-linux-x64/blender
IN=/opt/comfy/ComfyUI/input
PR="Turn this 3D render into a real photograph of a medieval stone castle under construction. Keep exactly the same camera angle, composition, the same rectangular curtain wall with its gate opening, the same wooden scaffolding and the same positions of every part, and add nothing else. The walls are built of real cut stone: rough-hewn grey limestone blocks laid in neat horizontal courses with visible mortar joints, irregular natural stone faces, slight weathering, sharp realistic detail. Bare brown dirt ground with a few piles of cut stone blocks, no lawn, no sand. Big live oak trees in the background. Bright natural daylight, neutral realistic colors, no text. The few small workers in orange vests are tiny and keep exactly their size."
for t in stone_brick_wall_001 large_sandstone_blocks_01 castle_brick_07; do
  [ -f out/F4_$t.png ] || TEX=$t ESC=3 $BL -b --factory-startup --python cena_castelo.py -- 4 out/F4_$t.png 1664 1248 96 2>&1 | grep -E "FASE_OK|Error|Traceback"
  sudo -n -u comfy cp out/F4_$t.png $IN/cs_F4_$t.png
  PROMPT="$PR" DENO=0.85 python3 -u roda_foto_srv.py cs_F4_$t.png cs_F4_$t 3 "bigly_merge_1.safetensors:0.7" 2>&1 | tail -2
done
echo T1_PRONTO
