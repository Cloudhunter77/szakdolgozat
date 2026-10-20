#!/bin/bash
# NYÁK-kép ellenőrzéshez: hardware/gen/pcbshow.sh <lap> <kimenet.png>
set -e
B=$1; O=$2; H=$(cd "$(dirname "$0")/.." && pwd)
T="$H/out/render"; mkdir -p "$T"
timeout 120 flatpak run --command=kicad-cli org.kicad.KiCad pcb export svg --mode-single --fit-page-to-board \
  --layers Edge.Cuts,F.Cu,F.Silkscreen,F.Courtyard,Dwgs.User,Cmts.User,F.Fab -o "$T/b.svg" "$H/$B/$B.kicad_pcb" >/dev/null
printf '<html><body style="margin:0;background:#fff"><img src="b.svg" style="width:1400px"></body></html>' > "$T/i.html"
timeout 90 google-chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1400,1900 --screenshot="$O" "file://$T/i.html" 2>/dev/null
python3 -c "
from PIL import Image; im=Image.open('$O').convert('RGB'); px=im.load(); W,H=im.size
ys=[y for y in range(H) if any(px[x,y]!=(255,255,255) for x in range(0,W,7))]
im.crop((0,0,W,(ys[-1]+10) if ys else H)).save('$O')"
