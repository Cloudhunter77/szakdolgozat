#!/usr/bin/env bash
# ModuNode Matter – segédscript.  Használat:  bash mt.sh <parancs>
#   setup   ESP-IDF v5.5.5 telepítése (~/esp alá), egyszer kell
#   build   fordítás (első alkalommal 15-30 perc, letölti az esp_matter komponenst)
#   erase   teljes flash törlés (ESPHome -> Matter váltáskor KÖTELEZŐ egyszer)
#   flash   feltöltés
#   log     soros log  [mp] [--reset]   pl.: bash mt.sh log 40 --reset
#   codes   párosító kódok lekérése a chip shelltől (csak UART porton megy)
#   clean   teljes build törlés
IDF_VER=v5.5.5
IDF_DIR="$HOME/esp/esp-idf-$IDF_VER"
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-$(ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | head -1)}"
PKGS=(git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0)

idf_env() {
  [ -f "$IDF_DIR/export.sh" ] || { echo "Nincs ESP-IDF. Előbb: bash mt.sh setup"; exit 1; }
  # shellcheck disable=SC1091
  . "$IDF_DIR/export.sh" >/dev/null || { echo "export.sh hiba – futtasd újra: bash mt.sh setup"; exit 1; }
}
need_port() { [ -n "$PORT" ] || { echo "Nincs soros port – dugd be a C6-ot (vagy PORT=/dev/ttyXXX bash mt.sh ...)"; exit 1; }; echo "Port: $PORT"; }

case "${1:-help}" in
  setup)
    missing=()
    for p in "${PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
    if [ ${#missing[@]} -gt 0 ]; then
      echo "Hiányzó csomagok. Futtasd a SAJÁT terminálodban, majd indítsd újra:"
      echo "  sudo apt install -y ${missing[*]}"
      exit 1
    fi
    if [ ! -d "$IDF_DIR" ]; then
      mkdir -p "$(dirname "$IDF_DIR")"
      git clone -b "$IDF_VER" --depth 1 --recursive --shallow-submodules \
        https://github.com/espressif/esp-idf.git "$IDF_DIR" || exit 1
    fi
    "$IDF_DIR/install.sh" esp32c6 && echo "ESP-IDF $IDF_VER kész."
    ;;
  build)
    idf_env; cd "$ROOT/firmware" || exit 1
    [ -f sdkconfig ] || idf.py set-target esp32c6 || exit 1
    idf.py build
    ;;
  erase) idf_env; need_port; cd "$ROOT/firmware" && idf.py -p "$PORT" erase-flash ;;
  flash) idf_env; need_port; cd "$ROOT/firmware" && idf.py -p "$PORT" flash ;;
  log)   idf_env; need_port; python "$ROOT/tools/serial_log.py" "$PORT" "${2:-30}" ${3:+"$3"} ;;
  codes) idf_env; need_port; python "$ROOT/tools/serial_log.py" "$PORT" 5 --cmd "matter onboardingcodes ble" ;;
  clean) idf_env; cd "$ROOT/firmware" && idf.py fullclean && rm -f sdkconfig ;;
  *) sed -n '2,10p' "$0" ;;
esac
