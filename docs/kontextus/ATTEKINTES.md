# Moduláris okosotthon platform (korábban ModuNode) – projekt áttekintés (Claude-nak)

> Ezt a fájlt a gyökér `CLAUDE.md` minden munkamenet elején betölti. Legyen **tömör és naprakész** (kb. 150 sor
> alatt): ha valami változik, itt is frissüljön; a részletek a specifikációkban, a `DONTESEK.md`-ben és a
> `beszelgetesek/`-ben. Utolsó frissítés: 2026-10-23.

## Cél
Szakdolgozat: **Moduláris okosotthon platform** (korábbi munkanév: ModuNode, D26). Egy **node** = ESP32-C6
vezérlő + JST-XH láncon csatlakozó **modulok** (LED, relé, általános bemeneti), mindegyik modulon saját STM32
(STM32L433RCT3, D78). A node **Matter-híd** (Thread / Wi-Fi / Ethernet) a **Home Assistant** felé, a modulok bridged
endpointok. ESPHome csak gyors demókhoz. Audió nincs a rendszerben (D29). **12–26 V-os tápra tervezünk (12 vagy 24 V, D71)**; a későbbi ötletek:
`V2-OTLETEK.md`.

## Aktuális állapot (2026-10-20)
- ✅ `firmware/esphome-demo` → `cp-01-esphome-demo` · ✅ `firmware/matter-c6` (Thread, HA-ba párosítva, szín csak
  részben) → `cp-02-matter-thread-ha` · ✅ breadboard 24 V-os LED-meghajtó, 2 csatorna (D15)
- 📝 CCT szalag firmware (D16): prompt kész, **még nincs lefuttatva**
- 🔌 Specifikációk: `MODULMAG-SPEC.md`, `VEZERLO-SPEC.md`. **Mind az öt KiCad-lap kész** (`hardware/`, generátorral); D71–D77 beépítve;
  NYÁK-ok előkészítve (körvonal, rétegek, kezdő elhelyezés – a huzalozást Balázs csinálja).
- 🔁 **D78–D80 (10-22):** modul-MCU **STM32L433RCT3**, modul-transceiver **SN65HVD230**, **N-FET a GND-ágban**, MCP9701A, zöld
  táp-LED a +5V-ról, AP2112K marad, 1 oz + fedetlen nagyáramú sávok (D82) – **rajzok lezárva (10-22)**; teljes ellenőrzés: `hardware/gen/ellenorzes.py` (0 hiba),
  a NYÁK-ok a rajzi szimbólumokra mutatnak (determinisztikus UUID-k); darabjegyzék: `hardware/bom/`; konzulensnek:
  `docs/komponenslista.md` + `hardware/out/kapcsolasi-rajzok-2026-10-23.pdf`. **Következik: layout (Balázs, 10-23 – 10-28).**
- 💰 **D84–D85 (10-22/23): legolcsóbb beszerzés** – minden az LCSC-ről a JLC-s NYÁK-rendeléssel (~15 eFt); a megszűnt NTD5C648NL /
  NTMFS5C604NL helyett NCE6080K / NCEP6090AGU; F201 NANO² 15 A → a LED-modul össz-árama 15 A; betáp-sorkapcsok DG128.
- ✏️ **D67:** a kézzel szerkesztett lapnál a `.kicad_sch` a forrás – **10-23 óta mind az öt lap kézi** (`hardware/gen/kezi-lapok.txt`;
  a `build.sh` ezeket csak ellenőrzi); munkafolyamat: `hardware/README.md`
- 📦 `SAMPLE-KERESEK.md` – TI kérés + rendelés leadva (10-19); a többi gyártó hátra (határidő 10-22)
- 📋 `NYAK-ELOKESZITES.md` – ami a rajz/layout előtt még nyitott
- ⏰ **NYÁK-rendelés legkésőbb ≈ 2026-10-31** (vezérlő + LED- + relé- + bemeneti modul, D25) – ütemterv: `UTEMTERV.md`
- 📄 A régi Design Reference és BOM a Windows-os `Documents\szakdolgozat` mappában van (nincs a repóban); a beadható
  2 oldalas docx-specifikáció **elavult** (még I²C/I²S busz, MCU nélküli modulok, audió).

## Architektúra (részletek: a két spec)
- **Busz (D28, D38, D52, D71):** JST-XH 4 tű – **1 V_BUS (5 V), 2 GND, 3 CAN_L, 4 CAN_H**, laponként 2 átmenő XH;
  nincs 24 V a láncon. **Közös föld, izoláció nincs (D71)**: a modulokon SN65HVD230 (kézben, −4…16 V – D79), a vezérlőn TCAN1044AV (±58 V). Lezárás: sima 120 Ω
  jumperrel, csak a lánc két végén. CAN-bitráta firmware-ből állítható (D34). Bekötési szabály: **a vezérlő és
  minden modul egy (12–26 V-os) tápról, csillagpontosan** (több lebegő SELV-táp is mehet, 0 V egy ponton – D77);
  busz-kábel AWG22. A busz-GND a modulon R-en át (LED-modul 1 Ω, a hurokáram ellen – D74); CAN-fojtó-hely minden lapon.
- **V_BUS = központi 5 V (D71):** a vezérlő adja **minden modul logikai tápját** – LMR33630 (5,2 V, 3 A) → LM66200
  (VAGY az USB-vel) → TPS2595 eFuse (**2 A**, 5,7 V-os vágás). **USB-ről is van V_BUS** (1–2 modul teszteléséhez).
  A modulon csak 5 V-os TVS (ESD); minden modul méri a hozzá jutó V_BUS-t (PC1).
- **Modul-MCU (D27 → D78):** **STM32L433RCT3** (75 db; LQFP64, lábra azonos az F303RET6-tal – 8 db tartalék a relé-/bemeneti
  laphoz); 1 ADC, nincs TIM8, 256 KB flash; CAN PA11/PA12; saját CAN-bootloader kell;
  MCU-független protokoll + vékony hardverréteg (`can_hw`, `pwm_hw`, `flash_hw`). Kvarc 8 MHz.
- **Modulmag tápja (D71, D80):** a busz +5V-ja → AP2112K-3.3 (kis ejtésű LDO, kerámiával stabil); 24 V a modulmagon nincs. A LED- és a
  relémodul a terheléshez saját 12–26 V-ot kap (VIN_SENSE a PB1-en), a bemeneti modulon nincs 24 V.
  A vezérlő LMR33630-a max. 36 V → **a tápot ≤ 26 V-ra állítani** (D57 marad).
- **HW-ID és HW_REV (D71):** 16 sáv (R_top 10 k + R_bottom): 0 = hiba, 1 LED, 2 relé (24 V-os tekercs), 3 bemeneti,
  4 relé (12 V-os tekercs), 5–14 későbbi, **15 = a firmware-ből megadott** (csak R_top).
- **Lábkiosztás (D54, D79; CubeMX-ben ellenőrizni):** modulmag: CAN PA11/12, USART3 PC4/5, SWD, HSE, HW-ID PC0,
  VBUS_SENSE PC1, LED PC13; VIN_SENSE (24 V) **PB1** a LED- és a relémodulon. LED-modul: TIM1 PA8–10 + TIM15 PB14/15 + TIM16 PB8,
  I_SENSE PA3 (COMP2 → TIM1/15/16 break), DAC1 PA4, DRV_EN PB12. Relé: PB12–15.
  Bemeneti: 16 bemenet külön EXTI-vonalon, I²C1 PB8/9.
- **Modulok (v1):**
  - **LED (D43, D47, D53):** 6 csatorna (2 × RGB / 3 × CCT / 6 × egyszínű), low-side → a közös vezeték a +24 V;
    3 × [+24 V, CHa, CHb]; 10 A/csatorna, össz. 15 A (D84: a J201 sorkapocs és F201); UCC27524 + 60 V-os FET, 25 kHz. Mérés: 24 V a biztosíték
    előtt/után, össz-áram (1 mΩ + INA181A2) → COMP2 + DAC-küszöb → TIM1/TIM15/TIM16 break (hardveres lekapcsolás).
    D65: FET NCE6080K (DPAK; D85 – az NTD5C648NL megszűnt), blokkbiztosíték a szalaghoz (D76), csatornánként gate- és drain-LED, drain → ADC.
    D78: polaritásvédelem **N-FET a GND-ágban** (NCEP6090AGU – D85, az LM74700 helyett), hőmérő **MCP9701A**; csavaros sorkapocs (D79).
  - **Relé (D62):** 4 × Schrack RTD14024 (16 A, 24 V DC) + ULN2803A; kimenet COM + NO (4 × 2 pólus);
    230 V-ra tervezve (≥ 8 mm + marás); fogyasztásmérés v2 (D37).
  - **Általános bemeneti (D44, D48, D51, D66):** 16 bemenet külön 3 tűs JST-PH-n; 10 k felhúzás a csatlakozó oldalán + 10 k soros + 10 nF (D75)
    (+ osztó-footprint 5/12/24 V-hoz) + ESD; 4 érzékelő-tápcsoport (3,3 / 5 V jumperrel, PTC-vel, külön 3,3 V-os
    LDO); HDC3020 a NYÁK-on + 4 tűs PH I²C-csatlakozó külső érzékelőhöz.
  - **Vezérlő (D45, D58–D61):** ESP32-C6-WROOM-1-N8 (D84; fém szekrénybe -1U, ugyanarra a footprintre – D63), W5500 +
    MagJack (opcionálisan beültetve), TCAN1044AV (±58 V), USB-C (táp busz nélkül), 2 XH, RGB LED + táp-LED;
    3,3 V: LMR36015; 5 V: LMR33630 + LM66200; V_BUS: TPS2595 (D71). Bemenet 12–26 V (F1 2 A, Q1 N-FET a GND-ágban – D78).
- **Mechanika (D50, javaslat):** DIN 43880-as ház-forma, a NYÁK a ház alján; felső váll: 24 V + busz + jumper,
  alsó váll: terepi csatlakozók, előlap: LED-ek fényvezetővel. 4 M (~66 × 85 mm NYÁK) a vezérlő, LED- és
  relémodul, 6 M (~100 × 85 mm) a bemeneti modul. NYÁK: 4 réteg, SMD csak felül, stencil (D42).
- **Okos modulok (D20, D31):** UID-alapú címkiosztás, egységes regisztertábla, firmware-frissítés a buszon;
  protokoll CANopen-fogalmakkal (heartbeat, SDO/PDO-szerű, LSS-szerű).
- **Matter (D21):** Aggregator + modulonként Bridged Node endpoint (UID → endpoint az NVS-ben); új modul
  újrapárosítás nélkül. **Állapot (D22):** kiesésnél a modul tartja az utolsó állapotot.
- **Tűzvédelem (D30, javaslat):** biztosíték a forrás oldalán, LED-táp ágakra bontva (≤ 100 W/ág), rugós sorkapocs (LED-betáp: csavaros, D79/D84)
  + érvéghüvely, álmennyezetben V-0 vagy fém ház, relémodul elosztódobozban; a firmware-es hőmérés (MCP9701A) csak harmadik réteg.

## Hardver – amit tudni kell
**ESP32-C6:** egymagos 160 MHz RISC-V, **nincs PSRAM**, **nincs Classic BT** (BLE 5.3), Wi-Fi 6 **csak 2,4 GHz**,
802.15.4 (Thread/Zigbee – egyszerre csak az egyik), 2 TWAI, **nincs Ethernet-MAC** (→ W5500 SPI-n), egy ADC (GPIO0–6).
**Ethernet (W5500) + Thread egyszerre működik** (külön hardver); a Wi-Fi + Thread csak időosztással (közös 2,4 GHz-es rádió).
Nincs olyan ESP32, amiben Ethernet-MAC és 802.15.4 is van; a szűk keresztmetszet a RAM (nincs PSRAM).
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
- **D71 óta nincs a NYÁK-okon:** ISO1042, P78E05, NCP1117 (a készlet megmarad másra). **LMR36015** (csak a
  vezérlőn): VQFN-HR, reflow + stencil, a B (1 MHz) változat. **LMR33630ADDA:** HSOIC-8 PowerPAD.
- **XH vs. PH:** XH a busz (2,5 mm), PH az érzékelők (2,0 mm) – nem dughatók egymásba.
- **Ajtóérzékelés:** AH1911 Hall + mágnes (mágnesnél LOW = csukva).

**Készlet:** ~50 Schrack 24 V SPDT relé · 8 STM32F303RET6 (tartalék) · ~200 P78E05-1000 · NCP1117ST33 (tekercs) · 5 AH1911
(a komódhoz ≥ 6 kell) · 74HCT14D (36) · WS2812C-2020 · LM3940, LM2576S, ACS758, LM2902/2904, IRFR1205, BT137,
LH1522 · IRFP064N, FDP2532, IRL3713, IRF5305, SUM110P08 · W5500-modul (breadboard-teszthez) · reflow-kemence ·
**75 STM32L433RCT3** · **86 SN65HVD230D** · 105 MCP2517FD · 200 TC2117-3.3 · ~21 MCP9701A · 150 zöld 0603 LED (522 nm) ·
5 CT10 reed · 35 + 28 × 25 MHz-es oszcillátor · IRFR120N, BSS138, MCP121, TSR 1-2433, MFRC522, ATWINC1500 stb.
Részletek: `beszelgetesek/2026-10-14-alkatreszkeszlet-p78e05.md`, `…/2026-10-21-alkatreszkeszlet-2.md`. Az AliExpress-rendelésből kimaradt az
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
- [ ] **Beültetés előtt:** a relékimenet THT sorkapcsainak névleges értéke (≥ 16 A / 250 V, D83) és a magasságok a Gainta-ház
      vállához (relé ~16 mm, sorkapcsok, elkók); 12/24 V-os bemenethez az osztót beültetni (D66, D81 elvetve)
- [x] **CubeMX (L433):** a `gen/ellenorzes.py` fejsorból betölti és kódot generál – minden periféria inicializálódik (10-22);
      a COMP2 → TIM1/15/16 break-et a firmware állítja be
- [x] **TI-rendelés leadva** (2026-10-19) – a beérkezést figyelni; ami nem jön, azt a többi beszerzéssel együtt megrendelni
- [ ] **Sample-kérések:** TI-kérelem elküldve (BME-s e-mail, 11 típus); a többi gyártó hátra (`SAMPLE-KERESEK.md`, határidő
      2026-10-22); ha a TI elutasít: LMR36015 és W5500 megvenni
- [ ] **Rajz közben:** a két spec „ellenőrizni” fejezete (CubeMX; kvarcok CL-je; F1/USB-C/gombok típusa;
      ~~W5500 MDI-hálózat~~ ✅ (D72, WIZnet-referencia); MagJack lábkiosztása (KiCad Hanrun-szimbólum szerint); RGB LED + 74HCT14 vagy WS2812B-V5)
- [ ] **DIN-ház (D73):** Gainta D4MG, NYÁK 86,5 × 68 mm (bemeneti: 86,5 × 103 mm) ✅; hátra: vállmagasság és kivágások a ház rajzából
- [ ] 4 rétegű NYÁK ára a JLC-ajánlatkérőben (D42); stencil
- [ ] **Beszerzés (D85 – legolcsóbb):** minden az LCSC-ről, a JLC-s NYÁK-rendeléssel együtt – 99 tétel, ~15 eFt ÁFA-val;
      kosár: `hardware/bom/lcsc-kosar.csv` (lista: `beszerzes.csv`, `gen/beszerzes.py`); házak később (~8 eFt, Hestore); TI-rendelés 8;
      fiók-érzékelők (AH1911 / reed) később
- [ ] NYÁK: kapcsolási rajzok ✅ (lezárás 10-22), layout (Balázs, 10-26-ig), rendelés ≈ 10-30
- [ ] Firmware később (L433; a meglévő Nucleón / ST-Linkkel kezdhető – D85): LED-modul (önteszt, árammintavétel, 15 A-es korlát (D84), DAC-küszöb,
      kiégett biztosíték), csatorna-csoportok → Matter-lámpák; modul-protokoll + bootloader; vezérlő: V_BUS-kezelés
- [ ] CCT firmware (D16) a breadboardon (`cp-03-cct-szalag` javaslat); 16 W/m a két szín együtt vagy külön?
- [ ] HA: futás közben hozzáadott endpoint tesztje (matterjs-server #1016); Matter-színmód (HS/XY) az RGB-csoportokhoz
- [ ] `tools/serial_log.py`: ne resetelje a C6-ot porton nyitáskor
- [ ] Beadható specifikáció (docx) frissítése; névcsere (D26) a repóban (CLAUDE.md, README) és a dokumentumokban
- [ ] NE556-os panel 24 V-ra: van-e rajta stabilizátor? Ha nincs: 78L12; az IRL3713 helyére FDP2532
- [ ] Design Reference + BOM bekerüljön-e a repóba

## Hol mi van
- `DONTESEK.md` – döntésnapló, D01–D85 (a 2026-10-14-i számozás-összefésülés a fejlécben)
- `MODULMAG-SPEC.md` – a modulmag kapcsolási specifikációja (táp a buszról, STM32L433, SN65HVD230, busz, HW-ID, lábkiosztás, BOM)
- `VEZERLO-SPEC.md` – a vezérlő kapcsolási specifikációja (táp + USB, LMR33630, LM66200, TPS2595, C6, W5500, CAN, USB-C, BOM)
- `SAMPLE-KERESEK.md` – sample-lista gyártónként + ami kézben van + amit meg kell venni
- `NYAK-ELOKESZITES.md` – rajz/layout előtti teendők, mechanika, 4 réteg
- `UTEMTERV.md` – napra bontott ütemterv a NYÁK-rendelésig (10-14 → 10-31), pipálható
- `V2-OTLETEK.md` – a v1-ből kihagyott ötletek
- `NAPLO.md` – a helyi Claude Code munkanaplója
- `beszelgetesek/` – a claude.ai chatek jegyzetei (csak ha a téma előkerül); legutóbbiak: `2026-10-14-alkatreszkeszlet-p78e05.md`,
  `2026-10-14-vezerlo-spec.md`, `2026-10-21-alkatreszkeszlet-2.md` (benne „D74” = a mi D78-unk)
- `../matter-tanulasi-terv.md` – 4 órás Matter labor terv (klasszikus ESP32-re készült, a C6-ra igazítani)
