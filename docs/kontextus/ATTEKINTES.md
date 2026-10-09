# ModuNode – projekt áttekintés (Claude-nak)

> Ezt a fájlt a gyökér `CLAUDE.md` minden munkamenet elején betölti. Legyen **tömör és naprakész**:
> ha valami változik (döntés, állapot, nyitott kérdés), itt is frissüljön. Részletek: `DONTESEK.md`,
> `beszelgetesek/`, `NAPLO.md`. Utolsó frissítés: 2026-10-09.

## Cél
Szakdolgozat: **ModuNode – moduláris okosotthon platform**. Kis, egymással kombinálható node-ok
(relé, LED-meghajtó, bemenetek/érzékelők), ESP32-C6 alapon. A végleges irány **Matter over Thread**,
vezérlő a **Home Assistant**. Az ESPHome a gyors prototípusokhoz/demókhoz kell.

## Aktuális állapot (2026-10-09)
- ✅ `firmware/esphome-demo` – ESPHome vezérlő demó a C6-on, hardveren tesztelve → `cp-01-esphome-demo`
- ✅ `firmware/matter-c6` – ESP-Matter, Thread; párosítva HA-ba (+ Google), a board LED-je HA-ból vezérelhető (szín csak részben)
  → `cp-02-matter-thread-ha`. Következő: ModuNode endpointok (relé + ajtó) a gyári lámpa helyett
- 🔜 Breadboard áramkör (relé/LED kimenet, AH1911 ajtóérzékelő) a demóhoz
- 📄 A tervezési dokumentáció (`ModuNode-Design-Reference.md`) és a BOM (`ModuNode_Prototipus_BOM.xlsx`)
  egyelőre a Windows-os `Documents\szakdolgozat` mappában van, **nincs a repóban**.

## Hardver – amit tudni kell
**ESP32-C6:** egymagos 160 MHz RISC-V, **nincs PSRAM** (külső sem), **nincs Classic Bluetooth** (csak BLE 5.3),
WiFi 6 **csak 2,4 GHz**, IEEE 802.15.4 (Thread/Zigbee). A konfigok ESP32-C6-DevKitC-1 lábkiosztást feltételeznek
(a pontos lap típusa nincs rögzítve).

| Láb | Használat | Megjegyzés |
|---|---|---|
| GPIO8 | WS2812 RGB LED | strapping |
| GPIO9 | BOOT gomb | strapping |
| GPIO18 | Relé 1 / kimenet (demó) | |
| GPIO19 | Ajtó bemenet (demó) | belső felhúzás |
| kerülendő | GPIO4, 5, 8, 9, 15 (strapping) · 12–13 (USB) · 16–17 (UART0 konzol) | |

**Tervezési elvek (korábbi beszélgetésekből):**
- **Bekapcsoláskor minden kimenet biztosan KI.** A PCF8574 bootkor HIGH-ba áll (a relék meghúznak), ezért
  TCA9554/PCA9554 javasolt. Az NPN szintillesztő invertál, és boot alatt felvillantja a LED-et. Firmware-ben
  `restore_mode: ALWAYS_OFF`.
- **I²C címek:** a TCA9554/PCF8574 0x20–0x27, az „A” változatuk 0x38–0x3F → **ütközik az ADE7953-mal**.
- **24 V-os sín:** a MOSFET gate max. ±20 V → 12 V-os ág vagy zener (~15 V) kell. A 24 V-os sínhez legalább 40 V-os FET.
- **LED-meghajtás:** új tervben logic-level FET (pl. AO3400A) közvetlenül GPIO-ról. A meglévő nem logic-level
  FET-ek (IRFP064N, FDP2532) csak gate-driverrel (TC4427/MCP1416) vagy NPN + push-pull fokozattal.
- **Relék:** 24 V-os tekercs (nincs 3. tápsín), ULN2803A meghajtó, 4 csatornás board.
- **Ajtóérzékelés:** AH1911 Hall-kapcsoló + mágnes (push-pull, 1,6–5,5 V, mágnesnél LOW = csukva). A lézeres
  modul (40 mA, lézer) csak ott, ahova nem fér mágnes.

**Készlet (amiről szó volt):** ~50 db Schrack 24 V SPDT relé · 5 db AH1911 · 12 db lézeres közelítésérzékelő ·
IRFP064N, FDP2532, IRL3713, IRF5305, SUM110P08-11L · BC546B, 2N3904, BC857B · WNS20S100C Schottky ·
BTA225B-600B triac · NE556-os 12 V LED-szalag vezérlő panel · ATWINC1500 (ModuNode-hoz nem kell).

## Szoftver / környezet
- Fejlesztői gép: MSI laptop, **Linux Mint (Cinnamon)** dual boot. Balázs Linuxban kezdő.
- ESPHome 2026.9 venv: `~/.venvs/esphome` · ESP-IDF **v5.5.5**: `~/esp/esp-idf-v5.5.5`
- Matter: `espressif/esp_matter` ~1.5.0 (lockolva: 1.5.1) managed komponens (esp-matter `release/v1.6` példa alapján).
  Nem kell connectedhomeip klón, és chip-tool sincs.
- Otthoni Matter hálózat: **Home Assistant + Thread border router**. Párosítás a HA Companion appal
  (Androidon a teszt VID 0xFFF1 / PID 0x8000 kell a Google Home Developer Console-ba). HA Matter Server:
  OHF matter.js 1.4.0 add-on, **„Enable test-net DCL usage” bekapcsolva** (különben a teszt DAC-ot elutasítja).
- Repó: `Cloudhunter77/szakdolgozat`. Commit és push a laptopról, a helyi Claude Code-dal. Tervezés és
  megbeszélés a claude.ai „szakdolgozat” Projektben.

## Nyitott kérdések / teendők
- [x] Matter firmware első build + párosítás HA-ba (Thread) → `cp-02` (2026-10-09)
- [ ] ModuNode Matter endpointok: `on_off_plugin_unit` (relé, GPIO18) + `contact_sensor` (ajtó, GPIO19)
- [ ] `tools/serial_log.py`: ne resetelje a C6-ot porton nyitáskor (beépített USB)
- [ ] Matter LED driver: XY színmód (`MoveToColor`, `CurrentX`/`CurrentY`) kezelése – most csak piros/kék megy
- [ ] Schrack relék pontos típuskódja (RT314024 / RT114024 / RP310024?), DC tekercs-e, footprint → BOM és
      Design Reference §6 frissítése; a §8 board-méretbecslés (2×2, 55–65 × 40–45 mm) újragondolása
- [ ] PCF8574 → TCA9554 csere a relé boardon (javaslat, nincs véglegesítve)
- [ ] LED-szalag: 12 vagy 24 V, csatornánként hány A? (megválaszolatlan)
- [ ] NE556-os panel 24 V-ra: van-e rajta már stabilizátor (fekete, fém fülű alkatrész)? Ha nincs: 78L12 kell;
      az IRL3713 helyére FDP2532
- [ ] AH1911-ből csak 5 db van – több ajtóhoz rendelni kell
- [ ] Design Reference + BOM bekerüljön-e a repóba (`docs/`)

## Hol mi van
- `DONTESEK.md` – döntésnapló (mi, mikor, miért, honnan)
- `NAPLO.md` – a helyi Claude Code munkamenet-naplója
- `beszelgetesek/` – a claude.ai chatek jegyzetei (csak akkor olvasd, ha a téma előkerül)
- `../matter-tanulasi-terv.md` – 4 órás Matter labor terv. Klasszikus ESP32-re és esp-matter v1.5-re
  készült, a C6-ra igazítani kell.
