# ModuNode – moduláris okosotthon platform

Szakdolgozat: moduláris okosotthon node-ok ESP32-C6 mikrovezérlőn. A végleges irány Matter (over Thread)
Home Assistanttal; a köztes lépések ESPHome-on készültek.

## Szerkezet
| Mappa | Tartalom | Állapot |
|---|---|---|
| [`firmware/esphome-demo/`](firmware/esphome-demo/) | ESPHome vezérlő demó: relé, ajtóérzékelő, Kézi/Automata mód, webes felület | ✅ hardveren tesztelve |
| [`firmware/matter-c6/`](firmware/matter-c6/) | ESP-Matter alapú firmware, Matter over Thread, Home Assistant | ✅ párosítva HA-ba (cp-02) |
| [`docs/`](docs/) | Tervek, jegyzetek | |

A tesztelt, visszaállítható állapotok listája: [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Eszközök
- Hardver: ESP32-C6 (DevKitC-1 / Super Mini), Home Assistant + Thread border router
- ESPHome (Python venv), ESP-IDF v5.5.5 + `espressif/esp_matter` komponens
- Fejlesztői gép: Linux Mint

Az egyes alprojektek indítása a saját `README.md`-jükben van.

## Titkok
A WiFi jelszavak és kulcsok a `secrets.yaml` fájlokban vannak, ezek **nincsenek** a repóban.
Új gépen a `secrets.example.yaml`-ből kell létrehozni őket.
