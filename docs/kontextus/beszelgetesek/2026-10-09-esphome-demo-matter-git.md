# ESPHome demó, Matter projekt, verziókezelés – 2026-10-09

Forrás: claude.ai „szakdolgozat” Projekt, aznapi munkamenet (Claude a felhőből dolgozott, a laptopra fájlokat írt).

## ESPHome demó (`firmware/esphome-demo`) – cp-01
- Cél: még aznap bemutatható vezérlés a C6-on. ESPHome 2026.9.1-gyel validálva, a laptopon fordítva és flashelve.
  Balázs visszajelzése: „működik szépen”.
- Funkciók: Relé 1 (GPIO18), ajtó bemenet (GPIO19, AH1911 vagy jumper GND-re), Kézi/Automata üzemmód,
  lekapcsolási késleltetés, BOOT gomb (rövid = relé, ≥1,5 s = mód), RGB LED állapotjelzés, `web_server` v3
  (`local: true`, internet nélkül is megy), API + OTA titkosítással, fallback hotspot.
- Kulcsüzenet a bemutatóhoz: a döntés a node-on születik (edge logika), a web/HA csak megfigyel és paraméterez.
- A felhőben a PlatformIO registry tiltott volt, ezért ott csak validálni lehetett, fordítani nem.

## Matter projekt (`firmware/matter-c6`) – még teszteletlen
- Balázs Matter hálózata: **Home Assistant + Thread** → Thread build.
- Alap: esp-matter `release/v1.6` / `examples/managed_component_light` (commit b90027f). ESP-IDF **v5.5.5**,
  `espressif/esp_matter` ~1.5.0 a Component Managerből.
- Thread konfig: az upstream CI módszere (`sdkconfig.defaults.c6_thread` → `sdkconfig.defaults.esp32c6`), plusz
  DevKit LED (GPIO8) és gomb (GPIO9).
- `mt.sh` segédscript (setup/build/erase/flash/log). `idf.py monitor` TTY nélkül nem megy → `tools/serial_log.py`.
- Teszt párosító kód: `MT:Y.K9042C00KA0648G00` / 3497-011-2332 (dekódolással ellenőrizve). Androidon a
  VID 0xFFF1 / PID 0x8000 a Google Home Developer Console-ba kell.
- Ellenőrizve: a CHIP Kconfigban nincs vendor/product name opció (a név a HA-ban átírható).
- Következő fázis: `on_off_plugin_unit` (relé) + `contact_sensor` (ajtó) endpointok, helyi logikával.

## Verziókezelés és munkamód
- Repó: `Cloudhunter77/szakdolgozat`. Szerkezet: `firmware/esphome-demo`, `firmware/matter-c6`, `docs/`.
- Commit és push a laptopról, a helyi Claude Code-dal. Checkpoint = hardveren tesztelt állapot, annotált
  `cp-NN-*` tag + `CHECKPOINTS.md`.
- `.gitignore`: titkok, build kimenet. A `dependencies.lock` szándékosan commitolva van.
- **Szabály: minden módosító lépés előtt kérdezni.**
- A megbeszéltek a `docs/kontextus/`-ba kerülnek, és a claude.ai Projekt tudástárába is. Frissíti Claude
  (claude.ai chatek után) és a helyi Claude Code (`NAPLO.md`). A repó privát is lehet.
