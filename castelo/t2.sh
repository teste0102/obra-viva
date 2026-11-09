#!/bin/bash
cd ~/ferramentas/castelo
BL=~/blender/blender-4.5.15-linux-x64/blender
IN=/opt/comfy/ComfyUI/input
BASE="Turn this 3D render into a real photograph of a medieval stone castle under construction. Keep exactly the same camera angle, composition, shapes and positions of every part shown, and add nothing else. Real cut grey limestone blocks laid in neat horizontal courses with visible mortar joints, sharp realistic detail, straight clean edges. Bare brown dirt ground with a few piles of cut stone blocks, no lawn. Big live oak trees in the background. Bright natural daylight, neutral realistic colors, no text. The few small workers in orange vests are tiny and keep exactly their size. "
declare -A P
P[1]="$BASE The only construction is a low stone foundation plinth course wider than the future wall, laid flush with the ground in a rectangle, with a gap for the gate. No walls yet."
P[2]="$BASE The construction is a rectangular curtain wall of stone only three meters high with a gate gap, and wooden scaffolding along the front and right side. No battlements."
P[3]="$BASE The construction is a rectangular curtain wall of stone six meters high with a gate gap, and tall wooden scaffolding along the front and right side. No battlements."
P[5]="$BASE The curtain wall is nine meters high, finished, with evenly spaced rectangular stone battlements (merlons) along the whole top of every wall and a gate gap in the front wall with no battlements over the gap. No scaffolding, no towers."
P[6]="$BASE The finished stone curtain wall nine meters high has evenly spaced rectangular battlements along the top, and in the front wall a round stone gate arch with carved voussoir stones, filled with two heavy dark oak double doors reinforced with black iron straps and hinges, slightly open. Neat finished masonry around the gate. No scaffolding, no towers."
for i in 6 5 3 2 1; do
  F=cs_F${i}
  [ -f out/$F.png ] || TEX=castle_brick_07 ESC=3 $BL -b --factory-startup --python cena_castelo.py -- $i out/$F.png 1664 1248 96 2>&1 | grep -E "FASE_OK|Error|Traceback"
  sudo -n -u comfy cp out/$F.png $IN/$F.png
  PROMPT="${P[$i]}" DENO=0.85 python3 -u roda_foto_srv.py $F.png t2_F$i 3 "bigly_merge_1.safetensors:0.7" 2>&1 | tail -1
  echo FOTO_F$i
done
echo T2_PRONTO
