# ModuNode – projekt áttekintés (Claude-nak)

> Ezt a fájlt a gyökér `CLAUDE.md` minden munkamenet elején betölti. Legyen **tömör és naprakész**:
> ha valami változik (döntés, állapot, nyitott kérdés), itt is frissüljön. Részletek: `DONTESEK.md`,
> `beszelgetesek/`, `NAPLO.md`. Utolsó frissítés: 2026-10-11.

## Cél
Szakdolgozat: **ModuNode – moduláris okosotthon platform**. Egy **node** = ESP32-C6 vezérlő + JST-láncon
csatlakozó **modulok** (LED, relé, szenzor), mindegyik modulon saját STM32. A node-ok **Matter over Thread**
(vagy WiFi/Ethernet) kapcsolattal mennek a **Home Assistant**-hoz; a node Matter-híd, a modulok bridged
endpointok. Az ESPHome a gyors prototípusokhoz/demókhoz kell.

## Aktuális állapot (2026-10-11)
- ✅ `firmware/esphome-demo` – ESPHome vezérlő demó a C6-on, hardveren tesztelve → `cp-01-esphome-demo`
- ✅ `firmware/matter-c6` – ESP-Matter, Thread; párosítva HA-ba (+ Google), a board LED-je HA-ból vezérelhető
  (szín csak részben) → `cp-02-matter-thread-ha`
- ✅ Breadboard 24 V LED-meghajtó, 2 csatorna (GPIO20/21, NPN + FDP2532, ≤ 1 kHz), bemérve (D15)
- 📝 CCT szalag firmware (D16): Claude Code-prompt kész, **még nincs lefuttatva** – a breadboardos prototípushoz
- 📐 Végleges architektúra eldöntve (D17–D25): node + okos modulok, CAN-busz, Matter-híd
- ⏰ **NYÁK-rendelés legkésőbb ≈ 2026-10-31:** vezérlő + LED- + relé- + szenzormodul (D25)
- 📄 A tervezési dokumentáció (`ModuNode-Design-Reference.md`) és a BOM (`ModuNode_Prototipus_BOM.xlsx`)
  egyelőre a Windows-os `Documents\szakdolgozat` mappában van, **nincs a repóban**.

## Architektúra (D18–D23)
- Vezérlő–modul ≤ 0,5 m. **JST-XH, 4 tű: +24 V, GND, CAN_H, CAN_L.** Lezárás: 120 Ω a vezérlőn + lezáródugó
  a lánc végén.
- **Modul-busz: CAN** (C6: 2 TWAI vezérlő, CAN FD nélkül; transceiver pl. TCAN330). Feltétel: az STM32-ben legyen
  CAN, különben I²C + INT + láncvezeték.
- **Okos modulok:** automatikus címkiosztás az STM32 UID-jával, egységes regisztertábla, firmware-frissítés a buszon
  bootloaderrel. A NYÁK-on: SWD, BOOT0 pad, ≥ 64 KB flash.
- **Matter:** Aggregator + modulonként Bridged Node endpoint, Reachable attribútum, UID → endpoint az NVS-ben;
  új modul újrapárosítás nélkül. A váltás a mostani firmware-ről egyszer újrapárosítással jár.
- **Állapot:** busz- vagy vezérlőkiesésnél a modul tartja az utolsó állapotot; a hiteles állapot a vezérlőnél.
- **Táp:** a láncon csak logikai táp; nagyáramú modulnak saját sorkapocs + biztosíték; csillagpont; TVS + P-FET a
  24 V bemeneten; modulonként ≥ 60 V-os buck.
- **Közös „modulmag”:** STM32 + CAN transceiver + 60 V-os buck + 2 JST + SWD + állapot LED + lezáró jumper.

## Hardver – amit tudni kell
**ESP32-C6:** egymagos 160 MHz RISC-V, **nincs PSRAM** (külső sem), **nincs Classic Bluetooth** (csak BLE 5.3),
WiFi 6 **csak 2,4 GHz**, IEEE 802.15.4 (Thread/Zigbee), 2 TWAI (CAN) vezérlő. A konfigok ESP32-C6-DevKitC-1
lábkiosztást feltételeznek (a pontos lap típusa nincs rögzítve). A végleges NYÁK-ra tervezett modul: ESP32-C6-WROOM-1-N16 (16 MB flash).

| Láb | Használat | Megjegyzés |
|---|---|---|
| GPIO8 | WS2812 RGB LED | strapping; a D16 szerint állapotjelző lesz |
| GPIO9 | BOOT gomb | strapping |
| GPIO18 | Relé 1 / kimenet (demó) | |
| GPIO19 | Ajtó bemenet (demó) | belső felhúzás |
| GPIO20 | LED-szalag meleg (WW), breadboard | D16, nem végleges |
| GPIO21 | LED-szalag hideg (CW), breadboard | D16, nem végleges |
| kerülendő | GPIO4, 5, 8, 9, 15 (strapping) · 12–13 (USB) · 16–17 (UART0 konzol) | |

**Tervezési elvek:**
- **Bekapcsoláskor minden kimenet biztosan KI.** A PCF8574 bootkor HIGH-ba áll (a relék meghúznak). Az NPN
  szintillesztő invertál, és boot alatt felvillantja a LED-et. Firmware-ben `restore_mode: ALWAYS_OFF`.
- **I²C címek** (a modulon belüli buszon): a TCA9554/PCF8574 0x20–0x27, az „A” változatuk 0x38–0x3F →
  **ütközik az ADE7953-mal**.
- **24 V-os sín:** a MOSFET gate max. ±20 V → 12 V-os driver-táp. A 24 V-os sínhez **60 V-os FET** (a hosszú
  szalagvezeték tüskéi miatt).
- **LED-meghajtás (D17):** gate driver (UCC27524, 12 V) + 60 V-os normál FET (pl. IPD053N06N), 25 kHz,
  csatornánként 10 A; a PWM-et a modul STM32-je adja. A breadboardon NPN + FDP2532, ≤ 1 kHz (D15).
  A logic-level-FET-es irány (D06) elvetve.
- **EMC (D24):** fázistolás és frekvencia-dithering, 22–47 Ω gate-ellenállás, CAN ESD-dióda + osztott lezárás;
  snubber / CM fojtó / ferrit csak footprintként.
- **Relék:** 24 V-os tekercs (nincs 3. tápsín), ULN2803A meghajtó, 4 csatornás board. Az ULN2803A-t a modul
  STM32-je közvetlenül hajthatja.
- **Ajtóérzékelés:** AH1911 Hall-kapcsoló + mágnes (push-pull, 1,6–5,5 V, mágnesnél LOW = csukva). A lézeres
  modul (40 mA, lézer) csak ott, ahova nem fér mágnes.

**Készlet (amiről szó volt):** ~50 db Schrack 24 V SPDT relé · ~20 db STM32 (típus még nincs meg) · 5 db AH1911 ·
12 db lézeres közelítésérzékelő · IRFP064N, FDP2532, IRL3713, IRF5305, SUM110P08-11L · BC546B, 2N3904, BC857B ·
WNS20S100C Schottky · BTA225B-600B triac · NE556-os 12 V LED-szalag vezérlő panel · PCA9685 modul ·
ATWINC1500 (ModuNode-hoz nem kell). Reflow-kemence van.

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
- [ ] **Az STM32-k pontos típusa** (van-e CAN, mekkora a flash) → eldönti a buszt (D19). **Ez most blokkol.**
- [ ] **Sample-kérések most** (TI, ADI, onsemi, Würth, Coilcraft, Phoenix; lista:
      `beszelgetesek/2026-10-10-node-modul-architektura.md`), a szállítás 1–2 hét
- [ ] NYÁK: modulmag + vezérlő + 3 modul kapcsolási rajza (1. hét), layout (2. hét), rendelés ≈ 2026-10-31
- [ ] JST típus: XH (3 A/tű) vagy PH (2 A/tű); lezáródugó
- [ ] Modul-protokoll és regisztertábla specifikáció; bootloader (a NYÁK-rendelés után)
- [ ] HA: futás közben hozzáadott endpoint tesztje (matterjs-server #1016 / PR #1077)
- [ ] CCT firmware (D16) lefuttatása Claude Code-dal a breadboardon (checkpoint javaslat: `cp-03-cct-szalag`)
- [ ] CCT szalag: a 16 W/m a két szín együtt vagy színenként? (→ `CCT_MAX_SUM`); a 18 m-hez betáplálási pontok
- [ ] ModuNode Matter endpointok (relé, ajtó) → a bridge-architektúrában modulok bridged endpointjai lesznek (D21)
- [ ] `tools/serial_log.py`: ne resetelje a C6-ot porton nyitáskor (beépített USB)
- [ ] Matter LED driver: XY színmód – a D16 után okafogyott (az RGB LED állapotjelző lesz)
- [ ] Schrack relék pontos típuskódja (RT314024 / RT114024 / RP310024?), DC tekercs-e, footprint → BOM és
      Design Reference §6 frissítése; a §8 board-méretbecslés (2×2, 55–65 × 40–45 mm) újragondolása
- [ ] PCF8574 → TCA9554 (D04): valószínűleg okafogyott, mert a modul STM32-je hajtja az ULN2803A-t
- [x] LED-szalag: 24 V, CCT 3000/6000 K, 16 W/m, 18 m, 15 A-es táp (2026-10-10)
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
