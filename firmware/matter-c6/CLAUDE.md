# ModuNode Matter – ESP32-C6, Matter over Thread → Home Assistant

A felhasználó (Balázs) magyarul kommunikál, Linux Mint alatt dolgozik, Linuxban kezdő – a parancsokat röviden
magyarázd el. A szakdolgozat (ModuNode) végleges iránya Matter. A **mai cél**: kiderüljön, hogy a C6 fel tud-e
csatlakozni Balázs Matter hálózatára (**Home Assistant + Thread border router**), egyelőre a gyári példa alapján.

## Honnan jön a kód
- `firmware/` = `espressif/esp-matter`, `release/v1.6` ág, `examples/managed_component_light` (commit b90027f)
- Az `esp_matter` (~1.5.0) az **IDF Component Managerből** töltődik le build közben → **nem kell** az esp-matter és a
  connectedhomeip repót klónozni, és a host toolokat (chip-tool) sem kell lefordítani.
- ESP-IDF: **v5.5.5** (ezt írja elő a példa és a v1.6 CI), helye: `~/esp/esp-idf-v5.5.5`
- `components/app_reset/` = `examples/common/app_reset` másolata (BOOT 5 s → gyári visszaállítás)
- `common/utils/common_macros.h` = `examples/common/utils` másolata (csak ez a fejléc kell)

Eltérések az upstreamtől (szándékosak):
- `firmware/sdkconfig.defaults.esp32c6` = upstream `sdkconfig.defaults.c6_thread` + DevKit gomb/LED sorok
  (ugyanezt csinálja az upstream CI: `cp sdkconfig.defaults.c6_thread sdkconfig.defaults.esp32c6`) → **Thread** build
- `CMakeLists.txt`: projekt név `modunode_matter`, app_reset útvonal, a titkosított OTA blokk törölve (pem nincs)

Az eszköz: egy Extended Color Light endpoint → a board WS2812 LED-je (GPIO8). BOOT (GPIO9) rövid nyomás = ki/be,
5 s nyomva tartás = gyári visszaállítás (kilép a Matter fabricből).

## Parancsok (`mt.sh`)
```bash
bash mt.sh setup          # ESP-IDF v5.5.5 telepítés (egyszer; ~15 perc, ~3 GB)
bash mt.sh build          # első build 15–30 perc (esp_matter letöltés + CHIP fordítás)
bash mt.sh erase          # ESPHome → Matter váltáskor EGYSZER kötelező (más partíciós tábla)
bash mt.sh flash
bash mt.sh log 40 --reset # boot log; benne: "SetupQRCode: [MT:...]" és "Manual pairing code: [...]"
bash mt.sh codes          # párosító kódok a chip shelltől (csak a UART-hidas USB porton van bemenet)
bash mt.sh clean          # build + sdkconfig törlés
```
Port: automatikusan az első `/dev/ttyACM*`/`/dev/ttyUSB*`; felülírás: `PORT=/dev/ttyUSB0 bash mt.sh flash`.

Szabályok:
- **`idf.py monitor` itt nem működik** (nincs TTY) → `bash mt.sh log`.
- **`bash mt.sh log` a beépített USB porton (303a:1001) `--reset` nélkül is újraindítja a C6-ot** (port nyitáskor).
  Párosításnál ezért előbb a log, és csak a `Commissioning window opened` után jöhet a telefon.
- **`sudo`-t ne futtass** – írd ki a pontos parancsot, és Balázs futtatja a saját terminálában.
- Hosszú lépésnél (setup, első build) előre szólj, mennyi ideig tart; ne szakítsd meg.
- Ha `sdkconfig.defaults*`-t módosítasz, a meglévő `firmware/sdkconfig` felülírja → `bash mt.sh clean`, majd build.

## Párosító adatok (fejlesztői teszt értékek)
QR: `MT:Y.K9042C00KA0648G00` · manuális kód: `3497-011-2332` · passcode 20202021 · discriminator 3840 ·
VID 0xFFF1 / PID 0x8000. A `matter-qr.png` ezt tartalmazza (dekódolással ellenőrizve). A boot log a `SetupQRCode`-ot
**nem** írja ki (esp_matter 1.5); ellenőrzés az `Advertise commission parameter vendorID=65521 productID=32768
discriminator=3840` sorból (a passcode a teszt adatforrás alapértéke, 20202021).

## Párosítás Home Assistantba (Balázs csinálja a telefonon – README.md-ben lépésenként)
Előfeltétel: HA-ban Matter integráció + Thread integrációban a preferált hálózatnak van border routere; a Thread
hitelesítő adatok szinkronizálva a telefonra; Androidon a teszt eszköz (VID 0xFFF1 / PID 0x8000) felvéve a Google
Home Developer Console-ban – enélkül Androidon elhasal a párosítás.

Mit nézz a logban párosítás közben:
- `CHIPoBLE advertising started` → a telefon látja BLE-n
- `Commissioning ... PASE` / `CASE` sikeres, majd OpenThread role `child`/`router` → csatlakozott a Thread hálóra
- `SRP ... registered` / `Commissioning complete` → HA eléri, kész
- Ha a „Thread hálózathoz csatlakozás” lépésnél áll meg: a telefonon nincs (vagy nem a preferált) Thread
  dataset, vagy a telefon/C6 messze van a border routertől.
- Androidon **két fabric** jön létre: előbb a Google (`VendorId 0x6006`), majd a HA (`VendorId 0x134B`).
- Ha a HA lépés így bukik: `AttestationRequest successful` → `ArmFailSafe (0s)` → `Commissioning failed: 32`, akkor
  a HA Matter Server add-onban nincs bekapcsolva az **Enable test-net DCL usage** (a teszt DAC-ot nem fogadja el).
- Sikertelen próbálkozások után: BOOT 5 s (gyári reset), vagy `erase` + `flash`, és újra.

## Vissza ESPHome-ra
`../esphome-demo` mappában `esphome run modunode-c6.yaml --device /dev/ttyACM0` – felülírja a Matter firmware-t.

## Következő fázis (csak ha Balázs kéri)
A gyári lámpa helyett **Matter-híd** (D21, `docs/kontextus/DONTESEK.md`): a node ESP32-C6 vezérlő, a modulok
(LED, relé, szenzor; mindegyiken STM32F303RET6) CAN-buszon csatlakoznak, és bridged endpointként jelennek meg.
- Aggregator endpoint + modulonként Bridged Node endpoint (pl. `on_off_plugin_unit` a relének, `contact_sensor`
  az ajtónak, Color Temperature Light a CCT LED-modulnak). Minta: esp-matter `examples/bridge_apps/blemesh_bridge`.
- Bridged Device Basic Information: UniqueID = STM32 UID, **Reachable** (kihúzott modul → nem elérhető).
- UID → endpoint az NVS-ben; endpoint-ID-t nem használ újra. A bridge-re váltás egyszer újrapárosítással jár.
- Első lépés NYÁK nélkül: a DevKiten szimulált modulok (pl. BOOT gomb ad hozzá egyet) → kiderül, hogy a HA
  kezeli-e a futás közben hozzáadott endpointot (matterjs-server #1016 / PR #1077).
- GPIO/CAN eseményt ISR-ből ne közvetlenül `attribute::update`-tel írd, hanem `PlatformMgr().ScheduleWork`
  vagy saját task útján. Az RGB LED maradjon állapotjelző. Minden módosítás után build, és a logból ellenőrizd
  az endpointokat.
