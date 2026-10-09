#!/usr/bin/env bash
# ModuNode C6 – ESPHome telepítése és környezet-ellenőrzés (sudo nélkül fut)
set -uo pipefail
cd "$(dirname "$0")"

VENV="$HOME/.venvs/esphome"
ok()   { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }

echo "== ESPHome =="
if [ ! -x "$VENV/bin/esphome" ]; then
  mkdir -p "$(dirname "$VENV")"
  if ! python3 -m venv "$VENV" 2>/dev/null; then
    rm -rf "$VENV"
    warn "Hiányzik a python3-venv. Futtasd a saját terminálodban, majd indítsd újra ezt a scriptet:"
    echo "      sudo apt install -y python3-venv python3-pip"
    exit 1
  fi
  "$VENV/bin/pip" install -q --upgrade pip setuptools wheel
  echo "  ESPHome telepítése (1-2 perc)..."
  "$VENV/bin/pip" install -q esphome || { warn "ESPHome telepítés sikertelen"; exit 1; }
fi
ok "ESPHome: $("$VENV/bin/esphome" version)"

echo "== Soros port =="
if id -nG "$USER" | grep -qw dialout; then
  ok "dialout csoport tag vagy"
else
  warn "Nem vagy a dialout csoportban. Futtasd, majd jelentkezz ki és be:"
  echo "      sudo usermod -aG dialout \$USER"
fi
if dpkg -s brltty >/dev/null 2>&1; then
  warn "A brltty telepítve van – CH34x USB-UART-os boardnál elveheti a portot. Ha gond van:"
  echo "      sudo apt remove brltty"
fi
PORTS=$(ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true)
if [ -n "$PORTS" ]; then ok "Talált port(ok): $PORTS"; else warn "Nincs soros port – dugd be a C6-ot (adatkábellel!)"; fi
lsusb 2>/dev/null | grep -iE "303a:|1a86:|10c4:" | sed 's/^/      /'

echo "== secrets.yaml =="
if grep -q "IDE_A_WIFI" secrets.yaml; then
  warn "Töltsd ki a WiFi nevét és jelszavát a secrets.yaml-ban (csak 2,4 GHz-es hálózat!)"
else
  ok "WiFi adatok kitöltve"
fi

echo "== Konfig validálás =="
"$VENV/bin/esphome" config modunode-c6.yaml >/dev/null 2>&1 && ok "modunode-c6.yaml érvényes" \
  || warn "Validálási hiba – futtasd: $VENV/bin/esphome config modunode-c6.yaml"

echo
echo "Flashelés:  $VENV/bin/esphome run modunode-c6.yaml --device /dev/ttyACM0"
