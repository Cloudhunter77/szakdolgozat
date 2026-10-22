#!/bin/bash
# Darabjegyzék laponként (a rendeléshez): hardware/gen/bom.sh  →  hardware/bom/<lap>.csv
# Értékenként és footprintenként csoportosítva, a DNP-k nélkül; a „Megjegyzés” mező a típusválasztás indoka.
set -e
H=$(cd "$(dirname "$0")/.." && pwd)
K="timeout 120 flatpak run --command=kicad-cli org.kicad.KiCad"
mkdir -p "$H/bom"
for B in vezerlo led-modul rele-modul bemeneti-modul; do
  $K sch export bom --exclude-dnp --group-by "Value,Footprint" --ref-delimiter " " \
     --fields "Reference,Value,Footprint,\${QUANTITY},Megjegyzés" --labels "Jelölés,Érték,Footprint,Db,Megjegyzés" \
     -o "$H/bom/$B.csv" "$H/$B/$B.kicad_sch" >/dev/null
  echo "$B: $(($(wc -l < "$H/bom/$B.csv") - 1)) tétel → bom/$B.csv"
done
