# Checkpointok

Minden checkpoint egy **hardveren tesztelt**, működő állapot, annotált git taggel jelölve.
Visszaállás: `git switch -c <uj-ag> <tag>` · megtekintés: `git checkout <tag>` (vissza: `git switch main`)

| Tag | Dátum | Tartalom |
|---|---|---|
| `cp-01-esphome-demo` | 2026-10-09 | ESPHome vezérlő demó ESP32-C6-on |
| `cp-02-matter-thread-ha` | 2026-10-09 | Matter over Thread, párosítás Home Assistantba |

---

## cp-01-esphome-demo — 2026-10-09
**Mi működik**
- ESP32-C6 ESPHome firmware (`firmware/esphome-demo/modunode-c6.yaml`), webes kezelőfelület (`http://modunode-c6.local`)
- Relé 1 (GPIO18) kapcsolása weben és a BOOT gombbal
- Kézi / Automata üzemmód; Automata módban az ajtóérzékelő (GPIO19) vezérli a relét, csukás után állítható
  késleltetéssel kapcsol le
- RGB LED állapotjelzés, bootoláskor a relé mindig KI; a beállítások újraindítás után megmaradnak

**Hogyan lett tesztelve**
- Csupasz C6 boardon, Linux Mint alól USB-n flashelve; a vezérlés a webes felületről működött.

**Visszaállítás / újraépítés**
- `git checkout cp-01-esphome-demo` → `firmware/esphome-demo/README.md` szerint (`secrets.yaml` a
  `secrets.example.yaml`-ből)

---

## cp-02-matter-thread-ha — 2026-10-09
**Mi működik**
- ESP32-C6 Matter firmware (`firmware/matter-c6`, esp-matter `managed_component_light` alapon, ESP-IDF v5.5.5,
  `esp_matter` 1.5.1), Thread FTD build
- Párosítás Androidról a HA appal: Thread hálóra csatlakozik (routerré lép elő), két fabric: Google + Home Assistant
- A board RGB LED-je (Extended Color Light, endpoint 1) HA-ból vezérelhető: ki/be, fényerő
- BOOT rövid nyomás → ki/be, az állapot azonnal frissül a HA-ban; BOOT 5 s gyári visszaállítás → tiszta újrapárosítás
- **Ismert hiba:** a szín csak részben megy (piros, kék). A HA a színválasztóból XY koordinátát küld
  (`MoveToColor`), a driver (`app_driver.cpp`) viszont csak a hue/saturation és a színhőmérséklet attribútumot kezeli

**Hogyan lett tesztelve**
- ESP32-C6 board a beépített USB-n (`/dev/ttyACM0`), Linux Mint alól fordítva és flashelve (`mt.sh`)
- HA Companion app (Android), HA Matter Server (OHF matter.js 1.4.0); a lépések a soros logban ellenőrizve
  (PASE, attesztáció, AddNOC, Thread `child -> router`, `Commissioning completed successfully`), a LED szemmel

**Előfeltételek a környezetben**
- Google Home Developer Console: Matter integráció, Test VID 0xFFF1 / PID 0x8000, mentve („Ready to test”)
- HA → Matter Server add-on → **Enable test-net DCL usage** (különben a teszt DAC-ot elutasítja)

**Visszaállítás / újraépítés**
- `git checkout cp-02-matter-thread-ha` → `firmware/matter-c6/README.md` szerint: `bash mt.sh setup` → `build` →
  `erase` → `flash`, majd párosítás. Részletes összefoglaló: `docs/osszefoglalo-2026-10-09-matter-thread.md`
