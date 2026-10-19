#!/bin/bash
# Kapcsolási rajz generálása + ellenőrzés:  hardware/gen/build.sh <lap>   (modulmag | vezerlo | rele-modul)
#   1. a <lap>.py legenerálja a <lap>/<lap>.kicad_sch-t  ← FIGYELEM: felülírja a kézi elrendezést!
#   2. kicad-cli: upgrade (KiCad 10 formátum), ERC, netlista, PDF  → hardware/out/
#   3. footprint-ellenőrzés: minden alkatrésznek van-e footprintje, és létezik-e
# A KiCad-könyvtárak másolatát (gen/kilib/, nincs a repóban) az első futás tölti le a Flatpakból.
set -e
B=$1; G=$(cd "$(dirname "$0")" && pwd); H=$(dirname "$G")
FP="flatpak run --command=sh org.kicad.KiCad"
K="timeout 180 flatpak run --command=kicad-cli org.kicad.KiCad"
mkdir -p "$G/kilib" "$H/out"
for l in 74xx 74xGxx Connector_Audio Connector_Generic Connector Converter_DCDC Device Diode Interface_CAN_LIN Interface_Ethernet Jumper LED \
         MCU_ST_STM32F3 power Power_Protection Regulator_Linear Relay RF_Module Switch Transistor_Array \
         Transistor_FET Driver_FET Amplifier_Current Power_Management; do
  [ -s "$G/kilib/$l.kicad_sym" ] || timeout 90 flatpak run --command=cat org.kicad.KiCad \
      /app/extensions/Library/symbols/$l.kicad_sym > "$G/kilib/$l.kicad_sym"
done
cd "$H"
python3 "$G/$B.py" "$B/$B.kicad_sch"
$K sch upgrade "$B/$B.kicad_sch" >/dev/null
$K sch erc --severity-all -o "out/$B-erc.rpt" "$B/$B.kicad_sch" | grep violations
grep -E "^\[" "out/$B-erc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c
$K sch export netlist -o "out/$B.net" "$B/$B.kicad_sch" >/dev/null
$K sch export pdf -o "out/$B.pdf" "$B/$B.kicad_sch" >/dev/null
python3 - "$H/out/$B.net" "$G" <<'PY' > "out/fp-$B.txt"
import sys; sys.path.insert(0, sys.argv[2])
import sx
n = sx.parse(open(sys.argv[1]).read())
for c in sx.find(sx.first(n, 'components'), 'comp'):
    f = sx.first(c, 'footprint'); print(sx.first(c, 'ref')[1], f[1] if f else '')
PY
awk '{print $2}' "out/fp-$B.txt" | sort -u | timeout 90 $FP -c 'while IFS=: read l f; do if [ -z "$l" ]; then echo "NINCS FOOTPRINT"; elif [ "$l" = modularis ]; then [ -f "'"$H"'/lib/modularis.pretty/$f.kicad_mod" ] && echo "OK $l:$f" || echo "HIÁNYZIK $l:$f"; else [ -f "/app/extensions/Library/footprints/$l.pretty/$f.kicad_mod" ] || echo "HIÁNYZIK $l:$f"; fi; done'
grep -E " $" "out/fp-$B.txt" | tr '\n' ' '; echo
