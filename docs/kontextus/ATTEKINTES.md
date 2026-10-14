# Moduláris okosotthon platform (korábban ModuNode) – projekt áttekintés (Claude-nak)

> Ezt a fájlt a gyökér `CLAUDE.md` minden munkamenet elején betölti. Legyen **tömör és naprakész** (kb. 150 sor
> alatt): ha valami változik, itt is frissüljön; a részletek a specifikációkban, a `DONTESEK.md`-ben és a
> `beszelgetesek/`-ben. Utolsó frissítés: 2026-10-14.

## Cél
Szakdolgozat: **Moduláris okosotthon platform** (korábbi munkanév: ModuNode, D26). Egy **node** = ESP32-C6
vezérlő + JST-XH láncon csatlakozó **modulok** (LED, relé, általános bemeneti), mindegyik modulon saját STM32
(STM32F303RET6). A node **Matter-híd** (Thread / Wi-Fi / Ethernet) a **Home Assistant** felé, a modulok bridged
endpointok. ESPHome csak gyors demókhoz. Audió nincs a rendszerben (D29). **24 V-ra tervezünk**; a későbbi ötletek:
`V2-OTLETEK.md`.

## Aktuális állapot (2026-10-14)
- ✅ `firmware/esphome-demo` → `cp-01-esphome-demo` · ✅ `firmware/matter-c6` (Thread, HA-ba párosítva, szín csak
  részben) → `cp-02-matter-thread-ha` · ✅ breadboard 24 V-os LED-meghajtó, 2 csatorna (D15)
- 📝 CCT szalag firmware (D16): prompt kész, **még nincs lefuttatva**
- 🔌 **Kapcsolási specifikációk készen (javaslat, függetlenül ellenőrizve):** `MODULMAG-SPEC.md` (a három modul közös
  magja, lábkiosztás mindhárom modulra) és `VEZERLO-SPEC.md` (ESP32-C6 vezérlő). Balázs 2026-10-13 óta rajzol KiCad-ben.
- 📦 `SAMPLE-KERESEK.md` – **most kell elküldeni a kéréseket** (TI az 1. prioritás)
- 📋 `NYAK-ELOKESZITES.md` – ami a rajz/layout előtt még nyitott
- ⏰ **NYÁK-rendelés legkésőbb ≈ 2026-10-31** (vezérlő + LED- + relé- + bemeneti modul, D25) – ütemterv: `UTEMTERV.md`
- 📄 A régi Design Reference és BOM a Windows-os `Documents\szakdolgozat` mappában van (nincs a repóban); a beadható
  2 oldalas docx-specifikáció **elavult** (még I²C/I²S busz, MCU nélküli modulok, audió).

## Architektúra (részletek: a két spec)
- **Busz (D28, D33, D38, D52):** JST-XH 4 tű – **1 V_BUS (5 V), 2 GND_BUS, 3 CAN_L, 4 CAN_H**, laponként 2 átmenő
  XH; nincs 24 V a láncon. Modulonként **galvanikusan leválasztott CAN** (ISO1042BDWVR, ±70 V, 5 kVrms – csak
  TI-sample-ből; ha nem jön: nem izolált breakout a padekre, D36). Lezárás: sima 120 Ω jumperrel, csak a lánc két
  végén. CAN-bitráta firmware-ből állítható (D34).
- **V_BUS:** a vezérlő adja – P78E05 (5,0 V ± 3 %) + TPS2553 (382/425/476 mA); a modulon legrosszabb esetben
  ~4,7 V (ISO1042: ≥ 4,5 V). Modul-oldali védelem: PTC 0,5 A + 5 V-os TVS; a 24 V-os félredugás elleni teljes
  védelem **nyitott (D55)**.
- **Modul-MCU (D27):** STM32F303RET6, 8 db; CAN PA11/PA12; saját CAN-bootloader kell (a ROM-é nem tud CAN-t);
  MCU-független protokoll + vékony hardverréteg (`can_hw`, `pwm_hw`, `flash_hw`). Kvarc 8 MHz.
- **Modulmag tápja (D56, D57):** 24 V → F1 → SS16 → (10 Ω) → SMBJ28A + **47 µF elkó (kötelező)** → P78E05 (5 V) →
  NCP1117 (3,3 V). A P78E05 max. 36 V → **a 24 V-os tápot ≤ 26 V-ra állítani.** A bemeneti modul a V_BUS-ról jár
  (TLV75533, B változat).
- **Lábkiosztás (D54, CubeMX-ben ellenőrizni):** modulmag: CAN PA11/12, USART1 PC4/5, SWD, HSE, HW-ID PC0,
  VIN_SENSE PC1, LED PC13. LED-modul: TIM1 PA8–10 + TIM8 PC6–8, I_SENSE PA7, DAC1 PA4, DRV_EN PB12. Relé: PB12–15.
  Bemeneti: 16 bemenet külön EXTI-vonalon, I²C1 PB8/9.
- **Modulok (v1):**
  - **LED (D43, D47, D53):** 6 csatorna (2 × RGB / 3 × CCT / 6 × egyszínű), low-side → a közös vezeték a +24 V;
    3 × [+24 V, CHa, CHb]; 10 A/csatorna, össz. 20 A; UCC27524 + 60 V-os FET, 25 kHz. Mérés: 24 V a biztosíték
    előtt/után, össz-áram (1 mΩ + INA181A2) → COMP2 + DAC-küszöb → TIM1/TIM8 break (hardveres lekapcsolás).
    A modulmag a 20 A-es főbiztosíték előtt ágazik le.
  - **Relé:** 4 Schrack relé + ULN2803A; típus és COM/NO/NC **nyitott**; fogyasztásmérés v2 (D37).
  - **Általános bemeneti (D44, D48, D51):** 16 bemenet külön 3 tűs JST-PH-n, bővítő tüske nélkül; soros R + ESD +
    opcionális osztó; HDC3020.
  - **Vezérlő (D45, D58–D61):** ESP32-C6-WROOM-1-N16 (fém szekrénybe -1U, ugyanarra a footprintre), W5500 +
    MagJack (opcionálisan beültetve), TCAN1044AV (±58 V), USB-C (táp busz nélkül), 2 XH, RGB LED + táp-LED;
    3,3 V: LMR36015; 5 V: P78E05. A V_BUS hardveresen csak 24 V mellett kapcsol be.
- **Mechanika (D50, javaslat):** DIN 43880-as ház-forma, a NYÁK a ház alján; felső váll: 24 V + busz + jumper,
  alsó váll: terepi csatlakozók, előlap: LED-ek fényvezetővel. 4 M (~66 × 85 mm NYÁK) a vezérlő, LED- és
  relémodul, 6 M (~100 × 85 mm) a bemeneti modul. NYÁK: 4 réteg, SMD csak felül, stencil (D42).
- **Okos modulok (D20, D31):** UID-alapú címkiosztás, egységes regisztertábla, firmware-frissítés a buszon;
  protokoll CANopen-fogalmakkal (heartbeat, SDO/PDO-szerű, LSS-szerű).
- **Matter (D21):** Aggregator + modulonként Bridged Node endpoint (UID → endpoint az NVS-ben); új modul
  újrapárosítás nélkül. **Állapot (D22):** kiesésnél a modul tartja az utolsó állapotot.
- **Tűzvédelem (D30, javaslat):** biztosíték a forrás oldalán, LED-táp ágakra bontva (≤ 100 W/ág), push-in sorkapocs
  + érvéghüvely, álmennyezetben V-0 vagy fém ház, relémodul elosztódobozban; firmware-NTC csak harmadik réteg.

## Hardver – amit tudni kell
**ESP32-C6:** egymagos 160 MHz RISC-V, **nincs PSRAM**, **nincs Classic BT** (BLE 5.3), Wi-Fi 6 **csak 2,4 GHz**,
802.15.4 (Thread/Zigbee – egyszerre csak az egyik), 2 TWAI, **nincs Ethernet-MAC** (→ W5500 SPI-n), egy ADC (GPIO0–6).
A demó-konfigok DevKitC-1-es lábakat feltételeznek:

| Láb (DevKit) | Használat | Megjegyzés |
|---|---|---|
| GPIO8 | WS2812 RGB LED | strapping; a D16 szerint állapotjelző |
| GPIO9 | BOOT gomb | strapping |
| GPIO18 / GPIO19 | relé (demó) / ajtó bemenet (demó) | a vezérlő NYÁK-ján CAN_TX / CAN_RX! |
| GPIO20 / GPIO21 | LED-szalag WW / CW (breadboard, D16) | a NYÁK-on VBUS_EN / VBUS_FAULT |
| kerülendő | GPIO4, 5, 8, 9, 15 (strapping) · 12–13 (USB) · 16–17 (UART0) | |

**Tervezési elvek:**
- **Bekapcsoláskor minden kimenet KI** (firmware: `restore_mode: ALWAYS_OFF`; a gate driverek EN-je lehúzva; a CAN
  TXD-k felhúzva → recesszív busz).
- **24 V-os sín:** 60 V-os FET, 12 V-os gate-driver-táp (MC78L12); EMC: fázistolás, dithering, gate-ellenállás,
  CM fojtó / snubber csak footprint (D24).
- **ISO1042:** DWV tok (7,5 mm széles test) – **nem a sima SOIC-8**; alatta az izolációs rés minden rétegen.
- **P78E05-1000:** SIP-3, 1 +VIN · 2 GND · 3 +VOUT, 8–36 V be, 10,4 mm magas. **NCP1117ST33:** SOT-223, kimenetén
  tantál (ESR ~33 mΩ–2,2 Ω). **LMR36015** (csak a vezérlőn): VQFN-HR, reflow + stencil, a B (1 MHz) változat.
- **XH vs. PH:** XH a busz (2,5 mm), PH az érzékelők (2,0 mm) – nem dughatók egymásba.
- **Ajtóérzékelés:** AH1911 Hall + mágnes (mágnesnél LOW = csukva).

**Készlet:** ~50 Schrack 24 V SPDT relé · 8 STM32F303RET6 · ~200 P78E05-1000 · NCP1117ST33 (tekercs) · 5 AH1911
(a komódhoz ≥ 6 kell) · 74HCT14D (36) · WS2812C-2020 · LM3940, LM2576S, ACS758, LM2902/2904, IRFR1205, BT137,
LH1522 · IRFP064N, FDP2532, IRL3713, IRF5305, SUM110P08 · W5500-modul (breadboard-teszthez) · reflow-kemence.
Részletek: `beszelgetesek/2026-10-14-alkatreszkeszlet-p78e05.md`. Az AliExpress-rendelésből kimaradt az
SCT-013-030 (v2) és az ULN2803A.

## Szoftver / környezet
- Fejlesztői gép: MSI laptop, **Linux Mint (Cinnamon)**; Balázs Linuxban kezdő. EDA: **KiCad**.
- ESPHome 2026.9 venv: `~/.venvs/esphome` · ESP-IDF **v5.5.5**: `~/esp/esp-idf-v5.5.5`
- Matter: `espressif/esp_matter` ~1.5.0 (lockolva: 1.5.1) managed komponens; nincs connectedhomeip klón, chip-tool sem.
- Otthon: **Home Assistant + Thread border router**; párosítás a HA Companion appal (Android: teszt VID 0xFFF1 /
  PID 0x8000 a Google Home Developer Console-ban); HA Matter Server: **„Enable test-net DCL usage” bekapcsolva**.
- Repó: `Cloudhunter77/szakdolgozat`; tervezés a claude.ai „szakdolgozat” Projektben – a `docs/kontextus/` a két
  hely közös anyaga (D13).

## Nyitott kérdések / teendők
- [ ] **Sample-kérések most** (`SAMPLE-KERESEK.md`); ha a TI elutasít: LMR36015 és W5500 megvenni, transceiverekhez
      tartalék (D36, D60)
- [ ] **D55** – V_BUS túlfeszültség-védelem: TVS + PTC marad, vagy TPS2660 minden modulon – Balázs dönt
- [ ] **Schrack relé** pontos típuskódja + COM/NO/NC – **blokkoló** a relémodulhoz
- [ ] **Rajz közben:** a két spec „ellenőrizni” fejezete (CubeMX; kvarcok CL-je; F1/F2/PTC/USB-C/gombok típusa;
      W5500 MDI-hálózat a WIZnet-referencián; MagJack lábkiosztása; RGB LED + 74HCT14 vagy WS2812B-V5)
- [ ] **DIN-ház kiválasztása** (pl. Camdenboss CNMB) → NYÁK-méret, furatok, vállmagasság (P78E05 + elkó!)
- [ ] 4 rétegű NYÁK ára a JLC-ajánlatkérőben (D42); stencil
- [ ] Beszerzés: AH1911 (+ mágnesek), W5500 + MagJack + 25 MHz, 1 mΩ-os sönt, JST-XH/PH, kvarcok, elkók, USB-C aljzat
- [ ] NYÁK: kapcsolási rajzok (10-13 – 10-19), layout (10-20 – 10-26), rendelés ≈ 10-31
- [ ] Firmware később: LED-modul (önteszt, árammintavétel, 20 A-es összegkorlát, DAC-küszöb, kiégett biztosíték
      jelzése), csatorna-csoportosítás a regisztertáblában → Matter-lámpák; modul-protokoll + bootloader; vezérlő:
      V_BUS-kezelés (VIN_SENSE / VBUS_SENSE / FAULT)
- [ ] CCT firmware (D16) a breadboardon (`cp-03-cct-szalag` javaslat); 16 W/m a két szín együtt vagy külön?
- [ ] HA: futás közben hozzáadott endpoint tesztje (matterjs-server #1016 / PR #1077); Matter-színmód (HS/XY) az
      RGB-csoportokhoz
- [ ] `tools/serial_log.py`: ne resetelje a C6-ot porton nyitáskor
- [ ] Beadható specifikáció (docx) frissítése; névcsere (D26) a repóban (CLAUDE.md, README) és a dokumentumokban
- [ ] NE556-os panel 24 V-ra: van-e rajta stabilizátor? Ha nincs: 78L12; az IRL3713 helyére FDP2532
- [ ] Design Reference + BOM bekerüljön-e a repóba

## Hol mi van
- `DONTESEK.md` – döntésnapló, D01–D61 (a 2026-10-14-i számozás-összefésülés a fejlécben)
- `MODULMAG-SPEC.md` – a modulmag kapcsolási specifikációja (táp, STM32, ISO1042, busz-oldal, lábkiosztás, BOM)
- `VEZERLO-SPEC.md` – a vezérlő kapcsolási specifikációja (táp + USB, P78E05, TPS2553, C6, W5500, CAN, USB-C, BOM)
- `SAMPLE-KERESEK.md` – sample-lista gyártónként + ami kézben van + amit meg kell venni
- `NYAK-ELOKESZITES.md` – rajz/layout előtti teendők, mechanika, 4 réteg
- `UTEMTERV.md` – napra bontott ütemterv a NYÁK-rendelésig (10-14 → 10-31), pipálható
- `V2-OTLETEK.md` – a v1-ből kihagyott ötletek
- `NAPLO.md` – a helyi Claude Code munkanaplója
- `beszelgetesek/` – a claude.ai chatek jegyzetei (csak ha a téma előkerül); legutóbbiak: `2026-10-13-can-izolacio-stm32f303.md`,
  `2026-10-13-nyak-elokeszites-modulmag.md`, `2026-10-14-alkatreszkeszlet-p78e05.md`, `2026-10-14-vezerlo-spec.md`
- `../matter-tanulasi-terv.md` – 4 órás Matter labor terv (klasszikus ESP32-re készült, a C6-ra igazítani)
