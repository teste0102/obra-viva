#!/bin/bash
cd ~/ferramentas/castelo
ESC="Small realistic stonemason workers, six feet tall, far from the camera, who keep exactly their small size; no larger people appear. "
IM=("castelo/t3_F1_v0_00001_.png [output]" "castelo/t2_F2_v0_00001_.png [output]" "castelo/t2_F3_v0_00001_.png [output]" "castelo/cs_F4_castle_brick_07_v0_00001_.png [output]" "castelo/t2_F5_v0_00001_.png [output]" "castelo/t2_F6_v0_00001_.png [output]")
T=("" "${ESC}Time-lapse of a medieval castle construction site. Masons lay neat courses of grey cut stone blocks with mortar, raising the curtain wall from the foundation to three meters, with wooden scaffolding. The wall stays a perfect rectangle with the same gate gap. Static camera, trees do not move." "${ESC}Time-lapse. Masons keep laying straight horizontal courses of grey stone blocks and the stone wall grows from three to six meters high, with scaffolding rising along it. Same rectangle and gate gap. Static camera, trees do not move." "${ESC}Time-lapse. Masons lay the last courses of grey stone blocks and the wall reaches nine meters high with wooden scaffolding along the front and right sides. Static camera, trees do not move." "${ESC}Time-lapse. Masons remove the scaffolding and build evenly spaced rectangular stone battlements along the whole top of the wall, the gate gap stays open. Static camera, trees do not move." "${ESC}Time-lapse. Masons build a round stone gate arch with carved stones in the gate gap, then carpenters hang two heavy dark oak doors with iron straps. Static camera, trees do not move, the wall and battlements do not change.")
for i in 1 2 3 4 5; do
  [ -f /opt/comfy/ComfyUI/output/castelo/c_seg_0${i}_00001_.mp4 ] && continue
  echo "SEG_$i inicio $(date +%H:%M)"
  python3 -u roda_flf_srv6.py "${IM[$((i-1))]}" "${IM[$i]}" $i "${T[$i]}" $((40+i)) 2>&1 | tail -1
  echo "SEG_${i}_FIM"
done
echo V1_PRONTO
