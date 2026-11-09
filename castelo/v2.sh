#!/bin/bash
cd ~/ferramentas/castelo
ESC="Small realistic stonemason workers, six feet tall, far from the camera, who keep exactly their small size; no larger people appear. No cars, no vehicles and no new objects appear anywhere. "
python3 -u roda_flf_srv6.py "castelo/t2_F2_v0_00001_.png [output]" "castelo/t2_F3_v0_00001_.png [output]" 2 "${ESC}Time-lapse. Masons keep laying straight horizontal courses of grey stone blocks and the stone wall grows from three to six meters high, with scaffolding rising along it. Same rectangle and gate gap. Static camera, trees do not move." 52 2>&1 | tail -1
echo V2_PRONTO
