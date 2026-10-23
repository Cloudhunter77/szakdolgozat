#!/bin/bash
# A konzulensnek szánt összefűzött PDF:  hardware/gen/pdf.sh  →  hardware/out/kapcsolasi-rajzok-<dátum>.pdf
# A mostani .kicad_sch fájlokból exportál (a rajzokhoz nem nyúl – D67), és minden lap egyszer szerepel, a komponenslista
# sorrendjében: vezérlő, modulmag, LED-modul, relémodul, bemeneti modul (a modulok PDF-jéből csak az 1. oldal; a 2. a modulmag).
set -e
H=$(cd "$(dirname "$0")/.." && pwd); cd "$H"
K="timeout 180 flatpak run --command=kicad-cli org.kicad.KiCad"
T="$H/out/pdf-tmp"; rm -rf "$T"; mkdir -p "$T"; trap 'rm -rf "$T"' EXIT   # a Flatpakos KiCad a /tmp-t nem látja
for B in vezerlo modulmag led-modul rele-modul bemeneti-modul; do
  $K sch export pdf -o "$T/$B.pdf" "$B/$B.kicad_sch" >/dev/null
  [ -s "$T/$B.pdf" ] || { echo "HIBA: $B PDF-exportja nem sikerült"; exit 1; }
done
for B in led-modul rele-modul bemeneti-modul; do
  pdfseparate -f 1 -l 1 "$T/$B.pdf" "$T/$B-1.pdf"
done
KI="out/kapcsolasi-rajzok-$(date +%F).pdf"
pdfunite "$T/vezerlo.pdf" "$T/modulmag.pdf" "$T/led-modul-1.pdf" "$T/rele-modul-1.pdf" "$T/bemeneti-modul-1.pdf" "$KI"
echo "$KI: $(pdfinfo "$KI" 2>/dev/null | awk '/Pages/{print $2}') oldal"
