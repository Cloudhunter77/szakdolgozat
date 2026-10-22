# Vezérlő (központi egység) – kapcsolási specifikáció (v1) – 2026-10-14, frissítve 2026-10-20 (D71), 2026-10-22 (D78)

A KiCad-rajz alapja, a `MODULMAG-SPEC.md` párja. Források: Espressif ESP32-C6-WROOM-1/1U adatlap v1.4, ESP32-C6
adatlap v1.5, hardvertervezési útmutató és KiCad-könyvtár; WIZnet W5500 adatlap v1.1.0 + referencia-kapcsolás;
TI adatlapok (LMR36015, TPS2553, TCAN1044A-Q1, TCAN330, ESD2CAN24-Q1); CUI P78E-1000; ST USBLC6-2; Microchip
MCP2561/2FD. Független ellenőrzés után javítva (2026-10-14). Állapot: **javaslat** – a 13. fejezet pontjait rajz
közben nézd át.

**Balázs döntései:**
- 2026-10-13 (D58): USB-C-ről is jár (busz nélkül) · 2 átmenő XH (a vezérlő a lánc végén vagy közepén is lehet) ·
  RGB LED + táp-LED · bővítő tüskesor nincs, csak debug.
- 2026-10-14: a V_BUS-t a kézben lévő **P78E05** adja (D59) · CAN transceiver: **TCAN1044AV** (D60).
- 2026-10-22 (D78): fordított polaritás ellen **Q1 N-FET a GND-ágban** a D1 (B360) helyett – a közös föld miatt (D71) a + ági
  dióda nem véd: fordított bekötésnél a busz GND-érén át zárlat lenne · a táp-LED (D5) a `+5V`-ról jár (zöld, 522 nm).
- 2026-10-22 (D84, legolcsóbb beszerzés): J1 Degson DG250 · L1/L3 FerroCore HPI0630 (saját footprint) · C40/C41 12 pF ·
  D3 SS56C · D9 BAT54HT1G · FB1 BLM18EG221 · C4 10 µF · C9 22 pF · U4 **N8** · SW1/SW2 PTS525 (a TL3342-footprinten).
- **2026-10-20 (D71, konzultáció után): központi 5 V.** A vezérlő adja az összes modul logikai tápját a buszon:
  **U2 LMR33630ADDA** (5,2 V, 3 A-es buck) → **U12 LM66200** (ideális dióda, az USB-vel VAGY-olva) → **U3 TPS259531**
  eFuse (2 A, 5,7 V-os vágás) → V_BUS. **USB-ről is van V_BUS** (1–2 modul teszteléséhez). Bemenet **12–26 V**.
  A 2.1, 2.3, 2.4 és a 11. fejezet ennek megfelelően; a modulok oldala: `MODULMAG-SPEC.md` (D71).

## 0. Tartalom

| Blokk | Fő alkatrész | Fejezet |
|---|---|---|
| 12–26 V-os bemenet, USB-táp külön ágon | F1 2 A, Q1 IRFR1205 a GND-ágban (D78), SS56C (D3, D84), SMBJ28A | 2.1 |
| 24 V (vagy USB) → 3,3 V (C6 + W5500) | LMR36015BRNXR (1 MHz, 1,5 A) | 2.2 |
| 12–26 V → 5,2 V (busz-táp, CAN, RGB LED) + USB-VAGY | LMR33630ADDA + LM66200 (D71) | 2.3 |
| V_BUS-eFuse, 2 A, 5,7 V-os vágás | TPS259531DSGR (D71) | 2.4 |
| MCU + rádió | ESP32-C6-WROOM-1-N8 (D84; fém szekrénybe: -1U, ugyanarra a footprintre) | 3 |
| Ethernet (opcionálisan beültetve) | W5500 + RJ45 MagJack + 25 MHz | 4 |
| CAN | TCAN1044AVDRQ1 (±58 V; tartalék: MCP2562FD, TCAN330, SN65HVD230) | 5 |
| Busz-oldal | 2 × JST-XH, ESD2CAN24-Q1, 120 Ω + jumper | 6 |
| USB-C | 16 tűs USB 2.0-s aljzat, USBLC6-2SC6 | 7 |
| Kezelőszervek, LED-ek, debug | RESET, BOOT, WS2812B-V5 + 74HCT14, 1 × 6-os tüskesor | 8 |

## 1. Netek

| Net | Mi | Megjegyzés |
|---|---|---|
| `+24V_IN` | a 24 V-os sorkapocs | |
| `+24V_P` | F1 után | csak 24 V-ról él; ezt méri a VIN_SENSE, ebből kapja az EN-t a V_BUS-kapcsoló |
| `+24V_F` | R7 után, az LMR33630 bemenete | szűrt, a TVS-sel |
| `VUSB` | az USB-C VBUS-a | |
| `VIN_BUCK` | az LMR36015 bemenete | `+24V_P` (D8-on át) VAGY `VUSB` (D3-on át) |
| `3V3` | C6, W5500 digitális, VIO | U1 |
| `3V3A` | a W5500 analóg tápja | `3V3`-ból FB1 ferriten át |
| `+5V_BUCK` | az LMR33630 kimenete (5,22 V) | az U12 VIN1-e |
| `+5V` | a CAN transceiver VCC-je, a TPS2595 bemenete, RGB LED + 74HCT14 | U12 (LM66200): a buckból **vagy USB-ről** (D71) |
| `V_BUS` | a lánc tápja (XH 1-es tű) | U3 kimenete |
| `GND` | közös föld = a busz GND-je (XH 2-es tű) | **közös föld minden modullal (D71)** |

A vezérlő földje így a tápjának, (USB-n) a laptopnak és – a D71 óta – minden modulnak a földje is. Az Ethernet a
trafón át leválasztott. Bekötési szabály: egy táp, csillagpontosan (D71).

## 2. Táp

### 2.1 Bemenet, USB-ág (D61)

```
+24V_IN → F1 → +24V_P ──────┬─ D2 SMBJ28A → GND        (J1 GND-pólusa → GND_IN → Q1 → GND, D78)
                             ├─ R1/R2 → VIN_SENSE (GPIO0)
                             ├─ D8 → VIN_BUCK → U1 (LMR36015) → 3V3
                             └─ R7 0 Ω → +24V_F ─ D7 SMBJ28A, C1 47 µF elkó, C2 10 µF → U2 (LMR33630) → +5V_BUCK ─┐
VUSB → D3 → VIN_BUCK                                                                           U12 LM66200 → +5V → U3 TPS2595 → V_BUS
VUSB ──────────────────────────────────────────────────────────────────────────────────────────┘   (D71)
```

- **Csak USB-ről** (24 V nélkül, D71): az USB a D3-on át az LMR36015-öt, az U12 VIN2-jén át a `+5V`-ot táplálja →
  a C6 + W5500 megy, és **a V_BUS is bekapcsol** (1–2 modul asztali teszteléséhez). Laptop-porton (0,5–0,9 A)
  csak néhány modul fér el; túlterhelésnél a port maga kapcsol le. A buck (+24V_F) oldala nem kap feszültséget,
  mert az U12 nem táplál vissza.
- **12 V-ról is működik (D71):** az LMR33630 (3,8 V-tól) és az LMR36015 (~4,2 V-tól) is jár; a szalag- és a
  tekercsfeszültség a modulokon a tápé (`MODULMAG-SPEC.md`, D71).
- **24 V-ról:** a D3 zár, az USB-portba nem jut feszültség.

| Ref | Alkatrész | Érték / típus | Megjegyzés |
|---|---|---|---|
| J1 | rugós sorkapocs, 2 pólus (Degson DG250-3.5-02P, 8 A – D84) | 24 V be | felső váll |
| F1 | SMD-biztosíték | **2 A** (D71), ≥ 32 V, gyors (1206) | 2 A-es buszterhelésnél 24 V-on ~0,6 A, 12 V-on ~1,2 A (11. fejezet) |
| Q1, R56, D12 | N-FET + gate-ellenállás + Zener | **IRFR1205** (55 V, ~27 mΩ, DPAK, kézben), 10 kΩ, BZT52C15 – D78 | a J1 GND-pólusa (`GND_IN`) és a lap GND-je között; helyes polaritásnál a gate a `+24V_P`-ről ~15 V-ot kap → vezet (12 V-on ~1,2 A → ~40 mW); fordítva zár, a GND-pólusra kerülő + nem jut a busz GND-jére. A korábbi D1 (B360) kikerült |
| D2 | TVS | SMBJ28A | `+24V_P` → GND; ~45 V-on fog (az LMR36015 60 V-os) |
| D8 | Schottky | SS16 (60 V, 1 A) | `+24V_P` → `VIN_BUCK`; az USB ne táplálja vissza a 24 V-os oldalt |
| D3 | Schottky | **SS56C** (60 V, 5 A, SMC – D84) | `VUSB` → `VIN_BUCK`. **60 V-os kell**: túlfeszültségnél a `VIN_BUCK` ~45 V is lehet, miközben a `VUSB` ~0 V. A 3 A-es dióda 0,5 A-en kisebbet ejt (~0,4 V) → USB-ről is meglegyen az LMR36015 4,2 V-ja |
| R7 | ellenállás | **0 Ω (D70)**; a 2512-es footprint marad, szükség esetén 10 Ω impulzusbíró | a C1-gyel RC-szűrő az U2 (LMR33630) elé, korlátozza a D7 áramát (D57 mintájára). Legrosszabb esetben ~0,16 A → 1,6 V, 0,26 W – ezért 2512 |
| D7 | TVS | SMBJ28A | `+24V_F` → GND – az LMR33630 max. 36 V-ja előtt |
| C1 | elektrolit – **kötelező** | 47 µF, 50 V, low-ESR, 105 °C | az R7-tel soros R-C a bemeneten → a betápkábel LC-lengését is csillapítja (D57) |
| C2 | kerámia | 10 µF, 50 V, X7R (1210) | az U2 VIN–PGND lábai mellett (+ C53 220 nF) |
| R1, R2, C3 | osztó | 150 kΩ / 10 kΩ, 100 nF | `+24V_P` → **GPIO0** (VIN_SENSE, ADC1_CH0): 24 V → 1,47 V; csak USB-ről 0 V |

**A tápot ne állítsd 26 V fölé** (D57 – az LMR33630 bemenete max. 36 V; D71).

### 2.2 3,3 V – U1: LMR36015BRNXR (1 MHz)
Lábkiosztása azonos az LMR36006 RNX-ével. A modulokon már nincs buck (D56), ez az egyetlen VQFN-HR a projektben.

| Ref | Alkatrész | Érték | Megjegyzés |
|---|---|---|---|
| C4 | kerámia | 10 µF, 50 V, X7R (1210) – D84 | `VIN_BUCK` |
| C5, C6 | kerámia | 220 nF, 50 V (0603) | egy-egy a 2-es és a 10-es VIN-lábnál |
| L1 | árnyékolt tekercs | **6,8 µH**, Isat ≥ 2,1 A – D84: FerroCore HPI0630-6R8 (Isat 4,9 A, 53 mΩ, 7,3 × 6,7 mm) | TI 10-1. táblázat, 1 MHz / 3,3 V |
| C7 | kerámia | 100 nF, ≥ 16 V | BOOT (4) – SW (12) |
| C8 | kerámia | 1 µF, 16 V | VCC (5) – AGND (6); más terhelés nem mehet rá |
| R3 | ellenállás | 100 kΩ 1 % | RFBT: `3V3` → FB |
| R4 | ellenállás | 43,2 kΩ 1 % | RFBB → 3,31 V (VFB = 1,0 V) |
| C9 | kerámia | 22 pF (D84) | CFF, R3-mal párhuzamosan |
| C10–C12 | kerámia | 3 × 22 µF, 10 V, X7R (1206) | az adatlap 3 × 15 µF-ot ad névlegesnek; DC-előfeszítés után ~3 × 15 µF |

Lábak (RNX): 1 PGND · 2 VIN · 3 NC → SW · 4 BOOT · 5 VCC · 6 AGND · 7 FB · 8 PG → **GND** · 9 EN → VIN ·
10 VIN · 11 PGND · 12 SW. Min. bekapcsolási idő max. 83 ns; 24 V → 3,3 V-on 137 ns – rendben. USB-ről (~4,4 V a
`VIN_BUCK`-on) a kimenet még szabályoz.

### 2.3 5 V – U2: LMR33630ADDA (400 kHz) + U12: LM66200 (D71)
TI 3,8–36 V-os, 3 A-es szinkron buck, HSOIC-8 PowerPAD (lábas tok). Értékek a TI adatlap 9-2./9-3. táblázata
szerint (5 V, 400 kHz), a kimenet 5,2 V-ra hangolva, hogy 24 V mellett biztosan ő tápláljon, ne az USB.

| Ref | Érték | Megjegyzés |
|---|---|---|
| C1, C2 | lásd 2.1 | bemenet (47 µF elkó + 10 µF / 50 V) |
| C53 | 220 nF, 50 V | CHF, közvetlenül a VIN (2) – PGND (1) lábaknál |
| C54 | 1 µF, 16 V | VCC (6) – csak ez kerülhet rá |
| C55 | 100 nF | BOOT (7) – SW (8) |
| L3 | **8,2 µH**, Isat ≥ 3,5 A, árnyékolt – D84: FerroCore HPI0630-8R2 (Isat 3,8 A, 59,5 mΩ; 2 A-en ~0,24 W) | TI: 8 µH |
| R54 / R55 | 100 kΩ / **23,7 kΩ** 1 % | VOUT = 1,0 V × (1 + 100/23,7) = **5,22 V** |
| C56–C59 | 4 × 22 µF, 10 V, X7R (1206) | |
| EN (3) | → VIN | UVLO belső |
| PG (4) | nem bekötve | (szabad GPIO nincs) |

**D10 SMBJ6.0A** a `+5V_BUCK`-on (D75): ha az U2 felső FET-je átüt, a 12–26 V a kimenetére kerülne – az LM66200 abs. max.
6 V, a TPS2595 abs. max. 20 V. A TVS ilyenkor rövidre zár, és az **F1 (2 A) kiolvad**; közben a TPS2595 a kimenetét 5,7 V-ra
vágja, így a buszra nem jut 24 V. Normál üzemben (5,22 V) a szivárgása < 1 mA.

**U12 LM66200DRLR** (TI kettős ideális dióda, SOT-583-8, 2 × 2,5 A, 40 mΩ, VIN max. 5,5 V, abs. 6 V):
3 VIN1 ← `+5V_BUCK` · 6 VIN2 ← `VUSB` · 4 ~ON → GND (mindig BE) · 2, 7 VOUT → `+5V` (+ C13 22 µF) · 1, 5 GND · 8 ST nem
bekötve. Mindig a nagyobb feszültségű bemenet táplál, a másikba nem folyik vissza áram – ez fontos, mert az USB
különben a buck kimenetén át a 24 V-os oldalt is feszültség alá helyezné (a felső FET testdiódáján át).

**A 24 V-os tápot ne állítsd 26 V fölé** (az LMR33630 bemenete max. 36 V – D57 marad).

### 2.4 V_BUS-eFuse – U3: TPS259531DSGR (WSON-8, 2 × 2 mm) (D71)
TI eFuse, 2,7–18 V (abs. 20 V), 0,5–4 A, **5,7 V-os túlfeszültség-vágás**, auto-retry, EN magas aktív.

| Láb | Név | Bekötés |
|---|---|---|
| 3, 4 | IN | `+5V` + C22 1 µF + C23 100 nF |
| 2 | EN/UVLO | **R10 100 kΩ a `+5V`-ról, R11 47 kΩ a GND-re** (5,2 V → 1,66 V; BE ~3,7 V felett) + **D9 BAT54** (anód az EN-en, katód a **GPIO20**-on – VBUS_EN) |
| 1 | dVdt | **C60 22 nF** → ~1,9 V/ms: 5 V ~2,7 ms alatt, 200 µF buszkapacitáson ~0,4 A bekapcsolási áram |
| 7 | ILM | **R12 = 1,02 kΩ 1 %** → `R = 2000 / (I − 0,04)` → **2,0 A**; a láb feszültsége a terhelőárammal arányos (276 µA/A) |
| 6 | FLT | **GPIO21** (VBUS_FAULT), R34 10 kΩ felhúzás a `3V3`-ra (nyitott drain) |
| 5 | OUT | `V_BUS` + C24 100 nF + C25 10 µF (16 V) |
| 8, PAD | GND | GND |

- **EN-logika (D71):** a V_BUS bekapcsol, amint bármelyik forrásból (24 V vagy USB) megvan az 5 V – a C6
  újraindulása alatt is. A firmware a GPIO20 alacsonyra húzásával kapcsolja KI (EN ≈ 0,3 V, a KI-küszöb 1,03 V) –
  pl. szándékos busz-újraindításhoz (ez minden modult újraindít).
- **Áramkorlát 2 A:** a modulok logikája + a bemeneti modul érzékelői (MODULMAG-SPEC 5.5). A nagy fogyasztók
  (szalag, relétekercs) a modul saját 12–26 V-járól mennek.
- **Túlfeszültség:** ha a `+5V` 5,7 V fölé menne, az eFuse vág – ez a modulok egyetlen túlfeszültség-védelme.
- **D4:** TVS, 5 V standoff (SMF5.0A): `V_BUS` → GND, a csatlakozók közelében.
- **R13, R14, C14:** 100 kΩ / 22 kΩ, 100 nF: `V_BUS` → **GPIO1** (VBUS_SENSE, ADC1_CH1): 5,2 V → 0,94 V.

## 3. ESP32-C6-WROOM-1-N8 (U4; D84 – a firmware 4 MB-os flashre van állítva)

### 3.1 Táp, EN, strapping-lábak
- **3V3 (2):** 22 µF + 100 nF közvetlenül a lábnál (Espressif periféria-kapcsolás).
- **EN (3):** R15 10 kΩ a `3V3`-ra + C15 1 µF a GND-re (RC-késleltetés) + **SW1 (RESET)** a GND-re + J5/5.
- **GPIO9 (15) – BOOT:** R16 10 kΩ felhúzás + **SW2 (BOOT)** a GND-re + J5/6; nagy kondenzátor ne legyen rajta.
  Üzem közben felhasználói gomb (D16: ki/be, Matter-gyári visszaállítás).
- **GPIO8 (10) – strapping + RGB LED:** R17 **10 kΩ felhúzás** – letöltési módhoz (GPIO9 = 0) a GPIO8-nak 1-nek
  kell lennie.
- **GPIO15 (23):** R18 10 kΩ felhúzás, nem használt (a JTAG-forrás-választás csak eFuse-zal élne).
- **GPIO4, GPIO5 (MTMS/MTDI):** csak SDIO-időzítést állítanak – szabadok, tesztpadra kivezetve.

### 3.2 Lábkiosztás

| Modul-láb | GPIO | Funkció | Külső elem |
|---|---|---|---|
| 1, 28, 29 | – | GND (29 = alsó pad, sok via) | |
| 2 | – | 3V3 | 22 µF + 100 nF |
| 3 | EN | reset | 10 kΩ / 1 µF, SW1 |
| 4 | GPIO4 | **LORA_DIO1** (D68) | – |
| 5 | GPIO5 | **EXP_GPIO5** → J8 bővítő (ADC1_CH5, D69) | DNP 4,7 kΩ fel / DNP le |
| 6 | GPIO6 | W5500 SCLK (FSPICLK, IO_MUX) | R19 0 Ω (33 Ω-hoz footprint) + kondenzátor-footprint a GND-re (nem beültetve) |
| 7 | GPIO7 | W5500 MOSI (FSPID, IO_MUX) | |
| 8 | GPIO0 | VIN_SENSE (ADC1_CH0) | 2.1 |
| 9 | GPIO1 | VBUS_SENSE (ADC1_CH1) | 2.4 |
| 10 | GPIO8 | RGB LED adat (strapping) | 10 kΩ felhúzás → 8. fejezet |
| 11 | GPIO10 | W5500 SCSn (GPIO-mátrixon) | 10 kΩ felhúzás |
| 12 | GPIO11 | W5500 RSTn **+ LoRa NRST** (közös, D68) | 10 kΩ felhúzás |
| 13 | GPIO12 | USB D− | 7. fejezet |
| 14 | GPIO13 | USB D+ | 7. fejezet |
| 15 | GPIO9 | BOOT gomb (strapping) | 10 kΩ felhúzás, SW2 |
| 16 | GPIO18 | CAN_TX (TWAI0) | 10 kΩ felhúzás (reset alatt recesszív) |
| 17 | GPIO19 | CAN_RX (TWAI0) | |
| 18 | GPIO20 | VBUS_EN (alacsony = V_BUS KI) | D9 BAT54 az EN felé (2.4) |
| 19 | GPIO21 | VBUS_FAULT | 10 kΩ felhúzás |
| 20 | GPIO22 | **LORA_CS** (D68) | R51 10 kΩ felhúzás (DNP) |
| 21 | GPIO23 | **LORA_BUSY** (D68) | – |
| 22 | – | NC | |
| 23 | GPIO15 | nem használt (strapping) | 10 kΩ felhúzás |
| 24 | GPIO17 | U0RXD (debug) | J5/4 |
| 25 | GPIO16 | U0TXD (debug) | **499 Ω soros** (Espressif ajánlás) → J5/3 |
| 26 | GPIO3 | W5500 INTn | 10 kΩ felhúzás |
| 27 | GPIO2 | W5500 MISO (FSPIQ, IO_MUX) | |

- Az SPI három gyors lába (CLK/MOSI/MISO) az IO_MUX-lábakon van; a CS a GPIO-mátrixon megy (az IO_MUX-os CS0 a
  GPIO16 = UART0 TX lenne). 40 MHz-ig a mátrix is ugyanúgy működik; a W5500 33,3 MHz-et garantál.
- A C6-ban **egy ADC van** (ADC1, GPIO0–6). A két mérés (1,47 V, 0,90 V) a **6 dB-es** csillapítással (0–~1,9 V)
  pontosabb, mint 12 dB-lel (0–3,3 V).
- A C6-ban két TWAI vezérlő van – a GPIO22/23 tesztpadjai egy későbbi második lánchoz maradnak.
- A régi demó-firmware (GPIO18 relé, GPIO19 ajtó, GPIO20/21 LED – breadboard) lábai ezen a lapon mást jelentenek.

### 3.3 Antenna és -1U
- **WROOM-1:** a modul antennás vége a NYÁK szélén túlnyúlik, vagy alatta és két oldalán kivágás; az antenna
  alatt **egyik rétegen se legyen réz**; a modul GND-padje körül sűrű via; ≥ 15 mm szabad tér fémtől (RJ45,
  sorkapocs, ház fém része).
- **WROOM-1U (fém szekrénybe):** a padjai – a GND-padet (EPAD, 29) is beleértve – pontosan ugyanott vannak, csak
  a modul rövidebb (18 × 19,2 mm a 18 × 25,5 helyett) → **ugyanarra a footprintre ültethető** (D63; az Espressif
  adatlap v1.4, 11-1. és 11-2. ábra: az EPAD közepe mindkettőn 7,495 mm-re a bal éltől és 12,29 mm-re az alsó
  éltől; az Espressif KiCad-footprintjei is egyeznek). A NYÁK-on a `modularis:ESP32-C6-WROOM-1` footprint, az
  antenna-kivágással. U.FL → kábel → SMA-aljzat a házon.

## 4. Ethernet – W5500 (U5, LQFP48, opcionálisan beültetve)

### 4.1 Lábak (W5500 adatlap v1.1.0)

| Láb | Név | Bekötés |
|---|---|---|
| 1 / 2 | TXN / TXP | MagJack TD− / TD+ (4.2) |
| 5 / 6 | RXN / RXP | MagJack RD− / RD+ (4.2) |
| 3, 9, 14, 16, 19, 48 | AGND | GND |
| 4, 8, 11, 15, 17, 21 | AVDD | `3V3A`, lábanként 100 nF |
| 7 | DNC | nem bekötni |
| 10 | EXRES1 | **12,4 kΩ 1 %** a GND-re, a lábhoz közel |
| 12, 13, 46, 47 | NC | nyitva |
| 18 | VBG | **nyitva** (lebegnie kell) |
| 20 | TOCAP | **4,7 µF** a GND-re, rövid úton |
| 22 | 1V2O | **10 nF** a GND-re |
| 23 | RSVD | **GND** |
| 24 | SPDLED | nyitva |
| 25 | LINKLED | MagJack zöld LED katódja; anód 330 Ω-on át a `3V3`-ra (aktív alacsony) |
| 26 | DUPLED | nyitva |
| 27 | ACTLED | MagJack sárga LED katódja; anód 330 Ω-on át a `3V3`-ra |
| 28 / 29 | VDD / GND | `3V3` + 100 nF / GND |
| 30 / 31 | XI / XO | Y1 25 MHz (±30 ppm) + 2 terhelőkondenzátor (4.3) |
| 32 | SCSn | GPIO10 + 10 kΩ felhúzás |
| 33 | SCLK | GPIO6 |
| 34 | MISO | GPIO2 |
| 35 | MOSI | GPIO7 |
| 36 | INTn | GPIO3 + 10 kΩ felhúzás |
| 37 | RSTn | GPIO11 + 10 kΩ felhúzás (min. 500 µs alacsony, utána ≤ 1 ms a PLL) |
| 38–42 | RSVD | **nyitva** (az adatlap v1.0.2 óta nem GND!) |
| 43, 44, 45 | PMODE2/1/0 | nyitva (belső felhúzás → 111 = minden mód, auto-negotiation); opcionális lehúzó-footprintek |

- **FB1:** ferritgyöngy `3V3` → `3V3A` (WIZnet: HH-1M1608-121JT, 120 Ω @ 100 MHz; D84: BLM18EG221TN1D, 220 Ω, 1 A).
- Hidegítés: 7 × 100 nF (AVDD-k + VDD) + 10 µF a `3V3`-on + 10 µF a `3V3A`-n.
- Áramfelvétel ~132 mA (100 Mbit adás). Nincs auto-MDIX – ma már szinte minden switch elintézi.

### 4.2 Hálózati illesztés (MDI) – a WIZnet „W5500-Ref-RJ45WithMag” referencia szerint (D72, 2026-10-20)

A referencia képe: https://docs.wiznet.io/assets/images/w5500_sch_v110_use_mag_-19e2939c3f018e5d72f1b957f990f96d.png –
a rajz ezzel lábról lábra összevetve (a breadboard-teszt elmaradt, D72).

| Ref | Érték | Bekötés (a referencia jelölése) |
|---|---|---|
| R20, R21 | 49,9 Ω 1 % | `ETH_TXP` és `ETH_TXN` → **`3V3A`** (ref. R2, R1); mellette C16 10 nF a `3V3A`-n (hidegítés) |
| R24 | 10 Ω 1 % | `3V3A` → a MagJack **TCT**-je (ref. R3), + C18 22 nF a GND-re (ref. C8) |
| R22, R23 | 49,9 Ω 1 % | `ETH_RXP_W` és `ETH_RXN_W` (a W5500 RX-lábai) → közös pont = **`ETH_RCT`** (ref. R6, R7) |
| C17 | 10 nF | `ETH_RCT` → GND (ref. C15); az `ETH_RCT` egyben a MagJack **RCT**-je |
| C19, C61 | 6,8 nF | **soros** az RX-vonalakban: W5500 RXP → C19 → RD+, RXN → C61 → RD− (ref. C9, C10) |
| C20 | 1 nF / 2 kV | `ETH_CGND` (a MagJack árnyékolása **és** 8-as lába – a Bob Smith-lezárás) → GND (ref. C16, CGND) |

- A TX-vonalakban a referencia opcionális 0 Ω-os csillapító-ellenállásokat (R21–R24) mutat EMC-hez – nálunk nincs,
  a 100 Mbit/s-os rövid vonalon nem szükséges.
- A LED-ek a referenciával egyeznek (anód a 3,3 V-on, katód 330 Ω-on át – nálunk az ellenállás az anód oldalán, ami
  egyenértékű).

**MagJack (J6):** WIZnet által használt: **CETUS J1B1211CCD** (1 TD+, 2 TCT, 3 TD−, 4 RD+, 5 RCT, 6 RD−, 7 NC,
8 GND, 9/10 zöld LED −/+, 11/12 sárga LED −/+, 13/14 árnyékolás). Olcsó, könnyen kapható: **HR911105A** – a
lábkiosztása eltér (egy KiCad-könyvtár szerint 1 TD+, 2 TD−, 3 RD+, 4 TCT, 5 RCT, 6 RD−), ezt a megvett darab
adatlapjából kell venni. A kapcsolási rajzon a jeleket funkció szerint kösd (TD±, TCT, RD±, RCT, LED-ek), a
lábszám a választott alkatrészből jön.

### 4.3 Kvarc
- **Y1:** 25 MHz, ±30 ppm (3225). A W5500 adatlapja CL = 18 pF-os kvarcot ír; a WIZnet-referencia 2 × 18 pF-ot
  használ. Általános szabály: C = 2 × (CL − 3…5 pF) – a megvett kvarc CL-jéből számold. **D84:** Kyocera CX3225FB25000F0FZZH1
  (CL = 10 pF, ESR ≤ 30 Ω, max. 100 µW) → C40/C41 = **12 pF**.
- Opcionális: 1 MΩ a kvarccal párhuzamosan (a WIZnet-referencián szerepel) – footprint, alapból nem beültetve.
- A W5500 lábai mellett, alatta csak GND.

## 5. CAN transceiver – U6: TCAN1044AVDRQ1 (SOIC-8) (D60)

**Miért nem a TCAN330:** a TCAN330 buszlábai csak **±14 V**-ot bírnak; a TCAN1044AV **±58 V**-ot (közel az ISO1042
±70 V-jához). A busz oldali 5 V így a modulokkal azonos szintű, a VIO-láb miatt a C6 felé 3,3 V-os. SOIC-8-ban
csak a -Q1 (autóipari) rendelési kód létezik: **TCAN1044AVDRQ1**.

| Láb | TCAN1044AV | Bekötés |
|---|---|---|
| 1 | TXD | GPIO18 + 10 kΩ felhúzás a `3V3`-ra |
| 2 | GND | GND |
| 3 | VCC | **JP2** (3 padas forrasztható jumper): alapból `5V`; a másik oldal `3V3` (3,3 V-os tartaléknak) · 100 nF + 1 µF |
| 4 | RXD | GPIO19 (VIO-szintű; táp nélkül nagyimpedanciás) |
| 5 | VIO | **JP3** (3 padas): alapból `3V3` (VIO); a másik oldal GND (a TCAN330 SHDN-je); SN65HVD230-nál nyitva · 100 nF |
| 6 | CANL | `CAN_L` |
| 7 | CANH | `CAN_H` |
| 8 | STB | **GND** (0 Ω-on át) – normál mód. A belső felhúzás miatt nyitva készenléti módba kerülne! |

**Tartalék ugyanarra a footprintre** (ha a TI-sample nem jön):

| Típus | JP2 (3-as láb) | JP3 (5-ös láb) | 8-as láb GND-n | Megjegyzés |
|---|---|---|---|---|
| TCAN1044AV | 5V | 3V3 (VIO) | STB → normál | **alap** |
| MCP2562FD (Microchip-sample) | 5V | 3V3 (VIO) | STBY → normál | lábról lábra azonos; buszlábak ±58 V |
| TCAN330 | **3V3** | GND (SHDN) | S → normál | ±14 V; az 5 V tönkretenné |
| SN65HVD230 | **3V3** | nyitva (Vref kimenet!) | Rs → nagy sebesség | breakoutról is |

- **A JP2 alapállása (5 V) a 3,3 V-os típusokat tönkreteszi** – a szitanyomatra írd ki: „5V: 1044/2562 · 3V3: 330/230”.
- **Soha ne legyen mindkét oldal összeforrasztva** egy 3 padas jumperen (a JP2-n ez az `5V`-ot a `3V3`-ra zárná).
- Áramfelvétel (5 V): domináns 45 mA tip. / 70 mA max. (60 Ω), buszhibánál ~130 mA.
- A TXD-domináns időkorlát (1,2–4 ms) miatt a legkisebb bitráta ~9,2 kbit/s.
- Csak USB-ről a `5V` nincs → a transceiver nem működik (a busz is ki van kapcsolva); a buszlábai ilyenkor
  nagyimpedanciásak.

## 6. Busz-oldal

### 6.1 J2, J3 – JST-XH, 4 tű (B4B-XH-A), átmenő
1 `V_BUS` · 2 `GND` · 3 `CAN_L` · 4 `CAN_H` – a két csatlakozó azonos tűi közvetlenül összekötve (mint a
modulokon). A vezérlő a lánc végén (a másik XH üres) vagy közepén is lehet.

### 6.2 U7 – ESD2CAN24-Q1 (SOT-23)
1 → `CAN_L` · 2 → `CAN_H` · 3 → GND (az 1 és 2 felcserélhető); J2/J3 mellett, rövid GND-bekötéssel.

### 6.3 Lezárás – JP1 + R25 (D52)
`CAN_H` → JP1 (2 tűs, jumper) → R25 120 Ω (0805) → `CAN_L`. **Bedugva, ha a vezérlő a lánc végén van**; ha a
közepén, akkor kihúzva, és a két lánc-vég modulján van bedugva.

### 6.4 Opcionális (D24)
Közös módusú CAN-fojtó footprintje a transceiver és a csatlakozók között – csak ha a mérés indokolja; v1-ben
áthidalva (a fojtó helyén két 0 Ω-os híd vagy forrasztható jumper).

## 7. USB-C (J4) – csak eszköz, csak táp-fogyasztó

**D11 SMF5.0A** a `VUSB`-n, az aljzat mellett (D75): USB-bedugáskor a kábel induktivitása és a kerámia-kondenzátorok miatt a
VBUS rövid ideig túllőhet – az LM66200 VIN2-je abs. max. 6 V.

| Jel | Bekötés |
|---|---|
| A6, B6 (D+) | összekötve → U8 → R26 **22 Ω** → GPIO13 |
| A7, B7 (D−) | összekötve → U8 → R27 **22 Ω** → GPIO12 |
| A5 (CC1) | R28 **5,1 kΩ** → GND |
| B5 (CC2) | R29 **5,1 kΩ** → GND (külön ellenállás, nem közös!) |
| A4, A9, B4, B9 (VBUS) | `VUSB` + **R30 2,2 kΩ** és **C21 1 µF** a GND-re |
| A1, A12, B1, B12 (GND) | GND |
| árnyékolás (shell) | GND |

- **R30 (2,2 kΩ):** 24 V-os üzemben a D3 szivárgása különben ~6 V-ra húzná a kihúzott aljzat VBUS-át; az USB-C-s
  laptopok csak ~0 V-os VBUS-ra kapcsolják rá a tápot.
- **U8 – USBLC6-2SC6 (SOT-23-6):** 1 és 6 = I/O1 (D+), 3 és 4 = I/O2 (D−), 5 = VBUS (`VUSB`), 2 = GND; az aljzat
  mellett.
- **R26, R27:** 22 Ω, a C6 modul közelében (Espressif: 22–33 Ω) + egy-egy kondenzátor-footprint a GND-re, nem
  beültetve. D+/D− 90 Ω-os differenciális pár, rövid.
- Programozás és konzol: a C6 beépített USB Serial/JTAG-ja (nincs külön USB-UART IC).
- Aljzat: 16 tűs USB 2.0-s Type-C (pl. HRO TYPE-C-31-M-12 vagy GCT USB4105) – a footprintet a választott típusból.

## 8. Kezelőszervek, LED-ek, debug
- **SW1 RESET, SW2 BOOT:** SMD nyomógomb (pl. 4 × 4 mm), az előlap felőli szélen – a házon tűvel/tolórúddal
  elérhetően.
- **D5 (táp):** `+5V` → 2,2 kΩ → zöld LED (522 nm, Vf ~3 V) → GND (USB-ről is világít) – D78: a 3,3 V-ról alig világítana.
- **D6 (RGB):** **WS2812B-V5** (vagy a kézben lévő WS2812C-2020): VDD ← **`5V`** + 100 nF; DOUT nyitva. A WS2812B
  3,7 V alatt nincs specifikálva, ezért nem a 3,3 V-ról jár. Fényvezető alá, az előlap felőli szélen. Csak 24 V-ról
  világít.
- **U9 – 74HCT14D (kézben, SOIC-14) szintillesztő:** VCC (14) ← `5V` + 100 nF, GND (7). GPIO8 → 1A (1); 1Y (2) → 2A (3);
  2Y (4) → R31 33 Ω → D6 DIN (két inverter sorban = nem invertál; a HCT bemenete a 3,3 V-ot biztosan magasnak
  látja). A nem használt 3A (5), 4A (9), 5A (11), 6A (13) a GND-re.
  **R32 (0 Ω, nem beültetve):** GPIO8 → DIN közvetlenül – a WS2812B-V5 bemenete 3,3 V-tal is működik, ilyenkor az
  U9 elhagyható. **U9 és R32 egyszerre ne legyen beültetve.**
- **RJ45-LED-ek:** link (zöld) és aktivitás (sárga) a W5500-ról (4.1) – ezek a vállon látszanak.
- **J5 – debug, 1 × 6, 2,54 mm (beültetés opcionális):** 1 `3V3` (R33 0 Ω-on át, **nem beültetve** – csak
  referencia; egy USB-UART átalakító 3,3 V-ja különben visszatáplálná a lapot) · 2 GND · 3 U0TXD (GPIO16, 499 Ω
  után) · 4 U0RXD (GPIO17) · 5 EN · 6 GPIO9 (BOOT). Ezzel egy USB-UART átalakítóval is programozható, ha az
  USB-C nem megy.

## 9. Teljes lábkiosztás – összefoglaló
Lásd 3.2. **Szabad láb már nincs** (D68/D69): GPIO4/22/23 a LoRáé, a GPIO5 a J8 bővítőé; a v2-es második CAN-lánc (TWAI1) lába így elfogyott. Strapping: GPIO8 (felhúzva), GPIO9 (felhúzva +
gomb), GPIO15 (felhúzva). Semmi nem ütközik az USB-vel (GPIO12/13) és az UART0-val (GPIO16/17).

## 10. Mechanika és layout (DIN 4 M, NYÁK ~66 × 85 mm – D50)
- **Felső váll:** J1 (24 V) · J2, J3 (busz) · JP1 (lezárás) · J4 (USB-C).
- **Alsó váll:** J6 (RJ45) – a hálózati kábel lefelé, a kábelcsatornába. (A felső vállon már nem fér el
  kényelmesen: 24 V ~10 mm + 2 × XH ~20 mm + jumper ~5 mm + USB-C ~9 mm + RJ45 ~16 mm ≈ 60 mm.)
- **Előlap felőli szél:** D5, D6 (fényvezető), SW1, SW2.
- **Antenna:** a WROOM-1 antennája egy sarokban, a lap szélén, minden fémtől (RJ45, sorkapocs) távol (3.3).
- **C1 (47 µF elkó):** 7,7 mm magas – a ház vállmagassága alá kell férnie. Az LMR33630 hűtőpadja alatt viák a GND-síkra.
- **Ethernet:** a W5500 a MagJack mellett; a TX/RX párok rövidek, 100 Ω-osak (JLC impedancia-kalkulátor, a
  választott rétegrendre), folytonos GND-sík fölött, via nélkül. A 25 MHz-es kvarc a W5500 lábainál.
- **USB:** D+/D− 90 Ω-os pár, az U8 az aljzatnál, az R26/R27 a C6-nál.
- **LMR36015:** C5/C6 közvetlenül a VIN–PGND lábaknál, kicsi SW-csomópont, az FB távol a SW-től, az AGND a PGND-vel
  egy ponton.
- **CAN:** U6 a J2/J3 közelében; a CANH/CANL párban.
- Rétegrend: jel / GND / táp / jel (D42); SMD csak felül.

## 11. Teljesítménymérleg (D71)

| Sín | Fogyasztó | Áram (csúcs) |
|---|---|---|
| `3V3` | C6 (Wi-Fi adás 382 mA; Thread 302 mA) + W5500 132 mA + LED-ek ~20 mA | **≈ 0,54 A** → LMR36015 (1,5 A) |
| `+5V` | V_BUS ≤ 2 A (korlát) + transceiver ≤ 70 mA + RGB LED ≤ 60 mA | **≤ 2,1 A** → LMR33630 (3 A) |
| `+24V_IN` (24 V) | (0,54 × 3,3 / 0,85 + 2,1 × 5,2 / 0,9) / ~23 V | **≈ 0,62 A**; 12 V-on **≈ 1,2 A** → F1 2 A, Q1 IRFR1205 (D78) |
| `VUSB` (csak USB) | C6-ág ~0,48 A + V_BUS (amennyit a port ad) | a port korlátozza |

## 12. Darabjegyzék (vezérlő)
U1 LMR36015BRNXR · U2 LMR33630ADDA · U12 LM66200DRLR · U3 TPS259531DSGR · L3 HPI0630-8R2 · U4 ESP32-C6-WROOM-1-N8 (vagy -1U) · U5 W5500 ·
U6 TCAN1044AVDRQ1 · U7 ESD2CAN24-Q1 · U8 USBLC6-2SC6 · U9 74HCT14D (kézben) · Y1 25 MHz (CX3225, CL 10 pF) · L1 HPI0630-6R8 ·
FB1 BLM18EG221 · F1 2 A / 32 V · D8 SS16 · Q1 IRFR1205 + R56 10 k + D12 BZT52C15 (D78) · D3 SS56C · D2, D7 SMBJ28A · D4 SMF5.0A ·
D9 BAT54HT1G · D5 zöld LED · D6 WS2812B-V5 (vagy WS2812C-2020) · J1 Degson DG250-3.5-02P · J2/J3 B4B-XH-A · J4 USB-C
(16 tűs) · J5 1 × 6 tüskesor · J6 MagJack (J1B1211CCD / HR911105A) · JP1 2 tűs + jumper · JP2/JP3 3 padas
forrasztható jumper · SW1/SW2 PTS525S5215A · kondenzátorok: 47 µF 50 V elektrolit (kötelező), 10 µF 50 V (1210, 2),
220 nF 50 V (2), 22 µF 10 V (4 + 1 a C6-nál), 100 nF (~18), 1 µF (5), 10 µF 16 V (3),
4,7 µF (TOCAP), 10 nF (2), 6,8 nF (2), 22 nF, 22 pF, 2 × 12 pF (kvarc), 1 nF / 2 kV · ellenállások: 470 k, 150 k,
100 k (2), 61,9 k, 47 k, 43,2 k, 22 k, 12,4 k, 10 k (~11), 5,1 k (2), 2,2 k (2), 499, 330 (2), 120, 49,9 (4), 33,
22 (2), 10 Ω (2512, impulzusbíró), 10 Ω (0603, 1 %), 0 Ω (4–5).

## 13. Rajz előtt / közben ellenőrizni
- [x] **W5500 MDI-hálózat** (4.2) a WIZnet-referencia szerint (D72).
- [ ] **MagJack** kiválasztása és a lábkiosztása (TCT és RCT külön lábon legyen).
- [ ] **RGB LED:** WS2812B-V5 közvetlenül (R32) vagy a kézben lévő WS2812C-2020 a 74HCT14-gyel (U9) – a választott
      LED adatlapja szerint.
- [ ] A 25 MHz-es kvarc CL-értéke → terhelőkondenzátorok.
- [ ] F1 (**2 A**, ≥ 32 V, D71), R7 (0 Ω, D70), D3 (60 V-os, kis esésű Schottky), USB-C aljzat és
      nyomógombok konkrét típusa → footprint.
- [ ] Footprintek: LMR36015 RNX (VQFN-HR), W5500 LQFP48 (7 × 7 mm), ESP32-C6-WROOM-1 (Espressif KiCad-könyvtár),
      BAT54 (a választott tok lábkiosztása). ✅ LMR36015, LM66200, TPS2595, E22 – a gyártói rajzokkal összevetve (10-20).
- [ ] A C1 és a többi magas alkatrész a Gainta D4MG vállmagassága alá (D73).
- [ ] A TCAN1044AVDRQ1 a TI-sample-listára (a TCAN330 helyett).

## 14. Változások a korábbi tervhez
- **D68–D70 (2026-10-19):** LoRa-előkészítés, bővítő és mérőpontok, 0 Ω-os R7, a spec szerinti DNP-pótlások – 15. fejezet.
- **D58** (Balázs, 2026-10-13): USB-C táp busz nélkül, 2 átmenő XH, RGB LED + táp-LED, csak debug-tüske.
- **D59** (Balázs, 2026-10-14): a V_BUS a P78E05-ről (5,0 V) az LMR36006 (5,2 V) helyett; a 3,3 V marad az LMR36015
  (D46 lezárva). A modulokon a V_BUS legrosszabb esetben ~4,7 V.
- **D60** (Balázs, 2026-10-14): TCAN1044AVDRQ1 a TCAN330 helyett, forrasztható jumperes tartalékkal.
- **D61** (javaslat): az USB külön diódás ágon csak a 3,3 V-os buckot táplálja; a V_BUS hardveresen csak 24 V mellett
  kapcsol be (EN-osztó a `+24V_P`-ről, GPIO20-ról letiltható); áramkorlát 61,9 kΩ (382/425/476 mA); RGB LED
  az 5 V-ról; lábkiosztás a 3.2 szerint.
- A független ellenőrzés javításai: D3 60 V-os dióda (a 40 V-os SS14 túlfeszültségnél tönkremehetne, és zárlatosan
  24 V-ot adna az USB-portra); VUSB-levezető ellenállás; a V_BUS alapértelmezett bekapcsolása USB-ről (táp-
  ingadozási hurok) megszüntetve; WS2812B az 5 V-ról; 22 Ω az USB-vonalakon; J5 3,3 V-ja csak referencia.

## 15. Kiegészítések a rajz átnézése után (2026-10-19, D68–D70)

### 15.1 LoRa – U10 Ebyte E22-900M22S (minden DNP, D68)
**EU-s adóteljesítmény (D77):** a 868 MHz-es sáv nagy részén 25 mW ERP (14 dBm) és 1 % kitöltés a határ; 22 dBm csak a
869,4–869,65 MHz-es alsávban (≤ 500 mW ERP, 10 %) szabályos – a firmware ezt korlátozza.

SX1262, 850–930 MHz (itt 868 MHz), 22 dBm, 14 × 20 mm, bélyeglyukas (saját footprint: `modularis:Ebyte_E22-900M22S`,
az Ebyte-kézikönyv méretrajzából; a padméret 1,8 × 0,9 mm saját választás).

| E22-láb | Jel | Bekötés |
|---|---|---|
| 9 VCC | `+3V3_LORA` | R46 0 Ω a `3V3`-ról (leválasztás / árammérés) + C51 10 µF + C52 100 nF |
| 19 NSS / 18 SCK / 17 MOSI / 16 MISO | SPI | LORA_CS (GPIO22, R51 10 kΩ fel) · a W5500-zal közös SCLK/MOSI/MISO |
| 15 NRST | `W5500_RST` | közös reset a W5500-zal (GPIO11) |
| 14 BUSY / 13 DIO1 | GPIO23 / GPIO4 | a DIO1 magas aktív → nem közösíthető a W5500 INTn-jével |
| 8 DIO2 → 7 TXEN; U11 74LVC1G04 → 6 RXEN | RF-kapcsoló | TXEN = DIO2, RXEN = ¬DIO2 → firmware: `setDio2AsRfSwitch(true)` |
| 21 ANT | J7 u.FL (Hirose U.FL-R-SMT-1) | rövid 50 Ω-os vonal, alatta folytonos GND; pigtail a ház SMA-jához |

Adáskor ~120 mA a 3,3 V-on (az LMR36015 1,5 A-es). A W5500 MISO-ja tri-state; a KiCad-szimbólumában „output”, ezért
a generátor tri-state-re írja át (ERC).

### 15.2 Bővítés és mérőpontok (D69)
- **J8** (JST-PH 3 tűs): 1 `3V3` · 2 GPIO5 · 3 GND; R52 4,7 kΩ felhúzás és R53 lehúzás/osztó – mindkettő DNP.
- **TP1–TP7:** `+24V_P`, `+5V`, `3V3`, `V_BUS`, `CAN_H`, `CAN_L`, GND.

### 15.3 A spec szerint eddig hiányzó DNP-footprintek
- **C49/C50** az USB D+/D− vonalon a C6 felőli oldalon (7. fejezet); **R47** 1 MΩ a 25 MHz-es kvarccal párhuzamosan (4.3);
  **R48–R50** PMODE-lehúzások (4.1); **L2** közös módusú CAN-fojtó + **JP4/JP5** alapból zárt áthidaló (6.4 –
  `CAN_H_T/CAN_L_T` a transceiver oldalán).
- **U1** saját footprint: `modularis:TI_VQFN-HR-12_RNX0012B` (a TI RNX0012B csomagrajzából).
- **Footprint-ellenőrzés (2026-10-20):** U1 (RNX0012B), U10 (E22 – két független referencia-footprinttel is: azonos lábsorrend, a padok ±7,0 mm-re igazítva), U12 LM66200 (SOT-583-8), U3 TPS2595 (DSG, ThermalVias) – a TI/Ebyte-rajzokkal egyeznek.

### 15.4 R7 = 0 Ω (D70)
A D57-féle 10 Ω helyett 0 Ω; a footprint marad. Bedugáskor a TVS nagyobb áramon, magasabban fog – a 24 V-os táp
≤ 26 V szabály ezért fontosabb.

