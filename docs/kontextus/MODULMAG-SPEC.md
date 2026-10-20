# Modulmag – kapcsolási specifikáció (v1) – 2026-10-13, frissítve 2026-10-20 (D71)

A KiCad-rajz alapja. A modulmag egy **hierarchikus lap**, amit a LED-, a relé- és a bemeneti modul ugyanabból a
fájlból használ. Lábszámok: ST hivatalos pin-adatai (STM32_open_pin_data, `STM32F303R(D-E)Tx.xml`); értékek: TI
adatlapok (ISO1042, TLV755P, ESD2CAN24-Q1, UCC27524, INA181), CUI P78E-1000, onsemi NCP1117, ST AN4206, STM32F3
HAL COMP-leírás. Független ellenőrzés után javítva (2026-10-13). **2026-10-14: a tápblokk P78E05 + NCP1117 lett
(D56, D57) – 2. fejezet; a vezérlő V_BUS-a 5,0 V (D59) – 5.5.** A busz másik oldala, a vezérlő: `VEZERLO-SPEC.md`.
Állapot: **javaslat** – a 11. fejezet pontjait rajz közben nézd át.

> **2026-10-20 – D71 (konzultáció után): központi 5 V, közös föld.** A modulmagon **nincs 24 V és nincs izoláció**: a
> logika a busz +5V-járól jár (AP2112K → 3,3 V), a CAN-transceiver **TCAN1044AV** (mint a vezérlőn), a busz GND-je
> a modul GND-je. A 2., 4., 5. és 6. fejezet ennek megfelelően átírva; a HW-ID 16 sávos (3.5). A 24 V-ot csak a
> LED- és a relémodul használja, a saját lapján (VIN_SENSE a PB11-en). Bekötési szabály: **a vezérlő és minden
> modul ugyanarról a (12–26 V-os) tápról jár, csillagpontosan**; busz-kábel AWG22.

## 0. Tartalom és változatok

| Blokk | Fő alkatrész | Fejezet |
|---|---|---|
| +5V (busz) → 3,3 V | AP2112K-3.3 | 2 |
| MCU + körítés | STM32F303RET6 (LQFP64), 8 MHz-es kvarc | 3 |
| CAN | TCAN1044AVDRQ1 | 4 |
| Busz | 2 × JST-XH, ESD2CAN24-Q1, 120 Ω + jumper, TVS | 5 |
| Debug | 1 × 7-es tüskesor (SWD + UART) | 3.6 |

- **Mindhárom modul a buszról kapja a logikai tápot (D71).** A LED- és a relémodul a terheléshez (szalag,
  tekercsek) saját 12–26 V-ot kap, a bemeneti modulon nincs 24 V.
- A korábbi A változat (P78E05 + NCP1117 a modulon, izolált ISO1042, `GND_BUS`) és a D66 opcionális buszos tápja
  (D6 + JP2) **elmarad**.

## 1. Netek

| Net | Honnan | Megjegyzés |
|---|---|---|
| `+5V` | J2/J3 1-es tű (a vezérlő V_BUS-a) | 4,5–5,2 V (a lánc végén kevesebb); a TCAN1044 VCC-je és az LDO bemenete |
| `+3V3`, `+3V3A` | U5 | MCU, VIO; VDDA ferriten át |
| `GND` | J2/J3 2-es tű + a modul saját GND-je | **közös föld** – a LED- és a relémodulon a 24 V-os GND is |
| `CAN_H`, `CAN_L` | J2/J3 4-es / 3-as tű | |

## 2. Tápblokk: +5V (busz) → 3,3 V – AP2112K (D71)

Lánc: `+5V` (J2/J3) → C2 → U5 AP2112K-3.3 → `+3V3` (C3). A vezérlő TPS2595 eFuse-a vágja a túlfeszültséget (5,7 V)
és korlátozza az áramot (2 A) – a modulon csak ESD-TVS van (5.2).

| Ref | Alkatrész | Érték / típus | Megjegyzés |
|---|---|---|---|
| C2 | kerámia | 10 µF, 16 V, X7R (0805) | a buszról érkező 5 V puffere |
| U5 | LDO | **AP2112K-3.3TRG1** (Diodes, SOT-23-5) | 1 VIN · 2 GND · 3 EN (→ VIN) · 4 NC · 5 VOUT; 600 mA, ejtés ~0,25 V 600 mA-en; bemenet abs. max. 6,5 V; disszipáció (5 − 3,3) V × ~0,1 A ≈ 0,17 W |
| C3 | kerámia | 10 µF, 10 V, X7R (0805) | az AP2112 kerámiával stabil (nem kell tantál) |
| R3, R4, C9 | osztó | 10 kΩ / 10 kΩ 1 %, 100 nF | `+5V` → **PC1** (VBUS_SENSE): 5 V → 2,5 V – a modul jelenti, mennyi busz-feszültség jut el hozzá |

- Áramszükséglet: STM32 ~40 mA + TCAN1044 (VCC: recesszív ~5 mA, domináns ~50–70 mA, csak adáskor) + LED-ek.
- A 3,3 V a lánc végén ~4,6 V-ig tart (0,25 V ejtés + tartalék); a TCAN1044-nek ≥ 4,5 V kell – ez a szűkebb.

## 3. STM32F303RET6 és körítése

### 3.1 Táplálás (ST AN4206)
| Láb | Név | Bekötés |
|---|---|---|
| 1 | VBAT | `3V3` + 100 nF (nincs elem) |
| 19, 32, 48, 64 | VDD | `3V3`, lábanként 100 nF + összesen 1 × 4,7 µF |
| 18, 31, 47, 63 | VSS | `GND` |
| 13 | VDDA (= VREF+ ezen a tokon) | `3V3`-ról **FB1**-en át, + 1 µF + 10 nF |
| 12 | VSSA | `GND` |

**FB1:** nagyon kis DC-ellenállású ferritgyöngy (≤ 0,1 Ω, 0603) **vagy 0 Ω** – ugyanarra a footprintre. Az ST
szerint a VDDA nem lehet kisebb a VDD-nél, és nem jöhet fel később; egy nagy ellenállású szűrő ezt megsértené.

### 3.2 Órajel
- **Y1:** 8 MHz-es kvarc (3225), PF0-OSC_IN (5) – PF1-OSC_OUT (6).
- **C10, C11:** terhelőkondenzátorok = 2 × (CL − 3…5 pF szórt kapacitás) – a kiválasztott kvarc CL értékéből.
  Pl. CL = 10 pF → ~12 pF; CL = 8 pF → ~8 pF.
- Közvetlenül a lábak mellé, alatta csak GND, más jel ne fusson alatta.

### 3.3 Reset és boot
- **NRST (7):** 100 nF a GND-re (belső felhúzás van); reset-gomb footprintje opcionális.
- **BOOT0 (60):** 10 kΩ a GND-re + egy tesztpad a `3V3`-hoz (tartalék; a programozás SWD-n megy).

### 3.4 Állapot-LED-ek
- **D3 (táp):** `3V3` → 2,2 kΩ → LED → GND.
- **D4 (állapot):** `3V3` → 1 kΩ → LED → **PC13** (2), aktív alacsony. A PC13 csak nyelni tud, legfeljebb ~3 mA-t
  (forrásként, LED meghajtására nem használható) – 1 kΩ-mal ~1,3 mA. **Piros vagy zöld LED** kell (a kék/fehér
  ekkora áramnál és 3,3 V-ról halvány).
- Mindkettő a NYÁK előlap felőli szélén, fényvezető alá (D50).

### 3.5 Hardverazonosító (HW-ID) – 16 sáv (D71)
3V3 – R_top – **PC0** (8) – R_bottom – GND, + 100 nF a PC0-n. **Az osztó és a 100 nF a modul saját lapján van**
(a modulmag csak a `HW_ID` hierarchikus jelet adja ki). **R_top mindig 10 kΩ**, a fajtát az R_bottom adja. A firmware
16 sávra osztja, kerekítve: `sáv = (ADC × 15 + 2047) / 4095` (12 bites ADC, egész osztás); névleges értékek:
k × 0,22 V, ± 0,11 V a sávhatárig. A mérés arányos (osztó és ADC is a 3,3 V-hoz viszonyít), 1 %-os ellenállással a
hiba néhány mV.

| Sáv | Modul | R_bottom (E96, 1 %) | Feszültség |
|---|---|---|---|
| 0 | **hiba** (hiányzó R_top / zárlat) | – | 0 V |
| 1 | LED | 715 Ω | 0,22 V |
| 2 | Relé, 24 V-os tekercs | 1,54 kΩ | 0,44 V |
| 3 | Bemeneti | 2,49 kΩ | 0,66 V |
| 4 | Relé, 12 V-os tekercs (12 V-os rendszerhez) | 3,65 kΩ | 0,88 V |
| 5–14 | későbbi modulok | R_b = 10 k × k / (15 − k) | k × 0,22 V |
| 15 | **a firmware-ből megadott** (csak az R_top van beültetve) | – | 3,3 V |

- **15. sáv:** a fajtát a firmware a flash egy beállításából olvassa (SWD-n vagy a buszon írható) – így ellenállás
  nélkül is lehet dolgozni. Ha nincs beírva semmi, a modul csak jelentkezik a buszon, **minden kimenete KI** marad.
- A relémodul a HW-ID-t összeveti a mért tápfeszültséggel (VIN_SENSE): 12 V-os relé ~16 V fölött nem kapcsol
  (hibát jelez), 24 V-os relé ~18 V alatt figyelmeztet.

### 3.6 Debug-csatlakozó (J1, 1 × 7, 2,54 mm – beültetés opcionális)
| J1 | Jel | MCU-láb |
|---|---|---|
| 1 | 3V3 (VTref) | – |
| 2 | SWCLK | PA14 (49) |
| 3 | GND | – |
| 4 | SWDIO | PA13 (46) |
| 5 | NRST | 7 |
| 6 | UART_TX (USART1) | PC4 (24) |
| 7 | UART_RX (USART1) | PC5 (25) |

ST-Link V2 klónhoz dupont-vezetékkel bekötve; a lap szélén, hozzáférhetően.

### 3.7 Revízió-azonosító és bővítő (D69)
- **HW_REV a PB0-n:** 3V3 – R10 10 kΩ – PB0 – R11 – GND, + C20 100 nF; ugyanaz a 16 sávos rendszer, mint a HW-ID-nél
  (3.5). **v1 = 1. sáv (R11 = 715 Ω)**; 0 = hiba, 15 = a firmware-ből megadott (D71).
- **J4** (2 × 5, 2,54 mm, DNP): 1 3V3 · 2 GND · 3 PA15 · 4 PB6 · 5 PB3 · 6 PB7 · 7 PB4 · 8 PB10 · 9 PB5 · 10 GND –
  SPI1 (PB3 SCK, PB4 MISO, PB5 MOSI, PA15 NSS), I²C1 alternatív lábai (PB6 SCL, PB7 SDA), PB10. A layoutnál dől el,
  hogy elfér-e.
- **Relémodul (a modul saját lapján):** J105 3,5 mm-es jack az SCT-013 lakatfogónak, R107/R108 10 k + C102 10 µF
  középfeszültség (1,65 V), R109 terhelő-ellenállás (csak áramkimenetes típushoz), R110 1 k + C103 10 nF → PA0. Minden DNP.

## 4. CAN – TCAN1044AVDRQ1 (U2) – közös föld (D71)
A vezérlővel azonos transceiver (`VEZERLO-SPEC.md` 5.), a KiCad-rajzon az MCP2562 szimbólumával (lábról lábra azonos).

| Láb | Név | Bekötés |
|---|---|---|
| 1 | TXD | **PA12** (45, CAN_TX) + **R1 10 kΩ felhúzás `3V3`-ra** (reset alatt recesszív busz) |
| 2 | GND | `GND` |
| 3 | VCC | `+5V` + C18 100 nF + C19 4,7 µF |
| 4 | RXD | **PA11** (44, CAN_RX) |
| 5 | VIO | `3V3` + C17 100 nF |
| 6 | CANL | `CAN_L` |
| 7 | CANH | `CAN_H` |
| 8 | STB | **R12 0 Ω** → GND (normál mód) |

- VCC 4,5–5,5 V; buszlábak ±58 V; a földkülönbséget a CAN közös módusú tartománya fedezi (néhány tized V a
  bekötési szabály mellett).
- **Miért nincs izoláció (D71):** a logika a buszról jár, így a modul GND-je eleve a busz GND-je – az ISO1042-nek
  nem lenne mit leválasztania. A LED-modul 20 A-es visszatérő árama a saját vastag tápvezetékén megy vissza, ha
  a bekötési szabályt (egy táp, csillagpont) betartjuk.

## 5. Busz

### 5.1 Csatlakozók – J2 (BUS_IN), J3 (BUS_OUT): JST-XH, 4 tű (B4B-XH-A)
| Tű | Jel |
|---|---|
| 1 | `+5V` (a vezérlő V_BUS-a) |
| 2 | `GND` |
| 3 | `CAN_L` |
| 4 | `CAN_H` |

J2 és J3 azonos tűi közvetlenül összekötve (átmenő busz). Az XH tűnként 3 A-t bír; a vezérlő 2 A-nél korlátoz.

### 5.2 Védelem a modulon
- **D5:** TVS, 5 V standoff (SMF5.0A): `+5V` → `GND`, a J2/J3 mellett – ESD és hot-plug tüskék ellen.
- Túlfeszültség és túláram ellen a vezérlő **TPS2595 eFuse-a** véd (5,7 V-os vágás, 2 A) – központilag, a modulokon
  nincs külön védelem (D71).

### 5.3 ESD – U3: ESD2CAN24-Q1 (SOT-23)
1 → `CAN_L` · 2 → `CAN_H` · 3 → `GND`. A J2/J3 közvetlen közelében, rövid, vastag GND-bekötéssel.

### 5.4 Lezárás – JP1 + R5 (D49, D52)
`CAN_H` → **JP1** (2 tűs, 2,54 mm, jumper) → **R5 120 Ω** (0805) → `CAN_L`.
Jumper bedugva = lezárva – **csak a lánc két végén** (a vezérlőn és az utolsó modulon).

### 5.5 Áram- és feszültségmérleg (D71)
- Modulonként ~50–100 mA (MCU + transceiver + LED-ek); a bemeneti modulon ehhez jönnek az érzékelők (csoportonként
  PTC 0,2 A). A vezérlő 2 A-t ad (`VEZERLO-SPEC.md` 2.4).
- Feszültség: a vezérlő 5,2 V-ot ad (USB-ről ~5,0 V). 1 m AWG24 oda-vissza ~0,17 Ω → 2 A-en ~0,34 V esés.
  **Busz-kábel: AWG22**, a nagy fogyasztású modulok a vezérlő közelében; a PC1 (VBUS_SENSE) mutatja, ha a lánc
  végén kevés marad (a TCAN1044-nek ≥ 4,5 V kell).

## 6. ~~A/B változat~~ – megszűnt (D71)
A korábbi A változat (saját 24 V → P78E05 → NCP1117, izolált ISO1042) és B változat (TLV75533 a V_BUS-ról) helyett
egyetlen kiépítés van: a 2. fejezet.

## 7. Lábkiosztás – minden modul egyszerre

A modulmag lábai minden modulon azonosak; a modulspecifikus lábak nem ütköznek velük. A bemeneti modul 16
bemenete 16 különböző lábszámon van → mindegyik saját EXTI-megszakítást kap. (Minden lábfunkciót az ST pin-adatai
alapján ellenőriztünk.)

| Láb | Port | Modulmag | LED-modul | Relémodul | Bemeneti modul |
|---|---|---|---|---|---|
| 2 | PC13 | STATUS-LED (nyelő) | | | |
| 5, 6 | PF0, PF1 | HSE 8 MHz | | | |
| 8 | PC0 | HW-ID (ADC1/2_IN6) | | | |
| 9 | PC1 | **VBUS_SENSE** (ADC1/2_IN7, D71) | | | |
| 10 | PC2 | | V_RAIL_SENSE (a főbiztosíték utáni 24 V, ADC1/2_IN8) | | |
| 11 | PC3 | | NTC (ADC1/2_IN9) | | |
| 14–17 | PA0–PA3 | | DS1–DS4 (drain-mérés, ADC1_IN1–4, D65) | | IN0–IN3 (ADC1_IN1–4) |
| 20 | PA4 | | **DAC1_OUT1 – foglalt** (a komparátor küszöbe; kívül nem bekötve, csak tesztpont) | | IN4 (ADC2_IN1) |
| 21, 22 | PA5, PA6 | | DS5, DS6 (drain-mérés, ADC2_IN2–3, D65) | | IN5, IN6 (ADC2_IN2–3) |
| 23 | PA7 | | **I_SENSE** (INA181 kimenet → ADC2_IN4 + COMP2_INP) | | IN7 (ADC2_IN4) |
| 24, 25 | PC4, PC5 | UART_TX/RX (USART1) | | | |
| 30 | PB11 | | **VIN_SENSE** (24 V az F201 előtt, ADC1_IN14 – D71) | **VIN_SENSE** (tekercs-táp, ADC1_IN14 – D71) | IN11 (ADC1/2_IN14) |
| 33 | PB12 | | DRV_EN (3 × UCC27524 EN) | REL1 | IN12 (ADC4_IN3) |
| 34–36 | PB13–PB15 | | | REL2–REL4 | IN13–IN15 (ADC3_IN5, ADC4_IN4, ADC4_IN5) |
| 37–39 | PC6–PC8 | | CH4–CH6 (TIM8_CH1–3) | | |
| 41–43 | PA8–PA10 | | CH1–CH3 (TIM1_CH1–3) | | IN8–IN10 |
| 44, 45 | PA11, PA12 | CAN_RX / CAN_TX | | | |
| 46, 49 | PA13, PA14 | SWDIO / SWCLK | | | |
| 60 | BOOT0 | 10 kΩ GND-re | | | |
| 61, 62 | PB8, PB9 | | | | I²C1 SCL/SDA (HDC3020) |
| 26 | PB0 | **HW_REV** (NYÁK-revízió, ADC – D69) | | | |
| 29, 50, 55–59 | PB10, PA15, PB3–PB7 | **J4 bővítő** (DNP, D69) | | | |
| 14 | PA0 | | | **CT_SENSE** (SCT-013, DNP – D69) | |
| egyéb | | szabad → firmware-ben analóg mód | | | |

Megjegyzések:
- **LED-modul túláramvédelem (D53):** I_SENSE a PA7-en a COMP2 nem invertáló bemenete. Az invertáló bemenet a
  **DAC1_OUT1** (PA4) – így a küszöb telepítésenként állítható (pl. a beállított max. áram 1,2-szerese, alapból
  ~22 A). Tartalék fix küszöbök: VREFINT ≈ 24 A, ¾ VREFINT ≈ 18 A, ½ VREFINT ≈ 12 A. A COMP2 kimenete belül a
  **TIM1 BKIN2 + TIM8 BKIN2** bemenetre (a HAL kombinált kimenet-választása). A PB12-n lévő TIM1_BKIN
  lábfunkciót **nem szabad** bekapcsolni (ott a DRV_EN van). Áramerősítő: **INA181A2 (×50)**, alacsony oldali sönt
  (1 mΩ, a közös GND-visszatérőben – a közös módusú feszültség ~0 V, az INA181 26 V-os határa nem gond):
  20 A → 1,0 V az ADC-n, kb. 66 A-ig mér. A firmware a COMP2-t és a DAC-ot a DRV_EN bekapcsolása **előtt**
  állítja be.
- **DRV_EN:** a három UCC27524 hat EN-lába közösen a PB12-re, **1 kΩ lehúzással** (minden EN belsőleg ~200 kΩ-mal a
  12 V-ra húz, a hat párhuzamosan ~33 kΩ; 1 kΩ-mal ~0,35 V, biztosan a 0,8 V-os küszöb alatt – a korábbi 4,7 kΩ-mal
  ~1,5 V lett volna, D65) → boot alatt a driverek tiltva. A driverek
  IN-lábain belső lehúzás van, a lebegő PWM-láb is KI-t jelent.
- **Relék:** a ULN2803A bemenetein opcionális 100 kΩ lehúzás (boot alatti lebegés ellen).
- A bemeneti modulon 12 bemenet ADC-képes (IN0–IN7, IN11–IN15), az IN8–IN10 csak digitális – de ezek (PA8–PA10)
  5 V-tűrők (FT); az ADC-s lábak TTa típusúak (≤ 3,6 V) → 5 V-os jelhez osztó (D66). A HDC3020 ALERT-je a PC2-n.
- **EXTI-ütközés (CubeMX-adatbázis, 2026-10-20):** a PC2 az EXTI2 vonalon osztozna az IN2-vel (PA2) – egy EXTI-vonal
  egyszerre csak egy porté. Ezért a HDC3020 ALERT-je **sima bemenet, a firmware lekérdezi** (a riasztás úgyis lassú
  esemény). Más lábra tenni sem segítene: az IN0–IN15 mind a 16 EXTI-vonalat lefoglalja.

## 8. Layout-irányelvek
- A modulmag **mindhárom lapon ugyanott**, a felső vállnál (D50). KiCad-ben a layoutot is újrahasználható
  blokként kezelni.
- **Busz** a felső él mentén: J2, J3, JP1, R5, U3, D5, a TCAN1044 és a VCC-kondenzátorai; izolációs rés nincs (D71).
  A busz GND-je és a modul GND-je egy sík – a LED-modulon a 20 A-es visszatérő út **ne** a busz-csatlakozók
  alatt menjen (a nagy áram a saját sorkapcsán lépjen ki).
- **U5 (AP2112K):** C2 és C3 közvetlenül a lábainál; SOT-23-5, kis disszipáció.
- **Kvarc:** a lábak mellett, GND-őrgyűrű, alatta semmi.
- **Hidegítés:** minden 100 nF a saját lábánál, a via a kondenzátor GND-oldalán.
- Debug-tüskesor a lap szélén; az állapot-LED-ek az előlap felőli szélen (fényvezető).

## 9. Darabjegyzék (egy modulmag, D71)
U5 AP2112K-3.3TRG1 · U2 TCAN1044AVDRQ1 · U3 ESD2CAN24-Q1 · STM32F303RET6 · Y1 8 MHz · D5 SMF5.0A ·
D3/D4 zöld/piros LED · J1 1 × 7 tüskesor · J2/J3 B4B-XH-A · JP1 2 tűs + jumper · FB1 ferrit (≤ 0,1 Ω) vagy 0 Ω ·
kondenzátorok: 10 µF 16 V (0805, 2 db), 100 nF (≈ 9 db), 1 µF, 4,7 µF (2), 10 nF, 2 × C_kvarc · ellenállások:
10 k (több, ebből R3/R4/R10 1 %), 715 Ω 1 % (R11), 0 Ω (R12), 1 k, 2,2 k, 120 Ω. (A HW-ID osztó a modul saját lapján van, 3.5.)

## 10. Változások a korábbi döntésekhez
- **Lezárás:** sima 120 Ω egy jumperrel, nem osztott (D49 pontosítva → D52).
- **INA181A3 → INA181A2**, a túláram-küszöb a DAC1-ről (PA4 foglalt a LED-modulon) → D53.
- **Lábkiosztás:** CAN = PA11/PA12, debug-UART = USART1 a PC4/PC5-ön (így a PA9/PA10 a TIM1-é marad),
  I²C1 = PB8/PB9 → D54.
- **A LED-modul logikai tápja a főbiztosíték előtt ágazik le** (saját F1-gyel) → a kiégett főbiztosíték jelezhető → D54.
- **V_BUS-védelem (2026-10-14):** nincs 24 V elleni védelem, a PTC (F2) kikerült, a TVS marad (ESD) → D55;
  a V_BUS-mérleg pontosítva (az ISO1042 csak adáskor húz 73 mA-t) → D64; a HW-ID osztó a modul lapjára, kerekítő
  sávképzés (3.5).
- **Tápblokk (2026-10-14): P78E05-1000 + NCP1117ST33** az LMR36006BRNXR helyett (kézben, ~200 db) → D56; a
  bemeneti elkó (C12) kötelező, opcionális R6 = 10 Ω, a 24 V-os táp ≤ 26 V → D57.
- **V_BUS (2026-10-14):** a vezérlőn P78E05 → 5,0 V ± 3 % (a korábbi 5,2 V helyett), a TPS2553 korlátja 61,9 kΩ-mal
  382/425/476 mA → D59, D61.
- **Központi 5 V (2026-10-20) → D71:** a fenti tápblokk, izoláció (ISO1042, `GND_BUS`) és buszos táp-opció (D66) helyett
  a modul a buszról jár (AP2112K), TCAN1044AV, közös föld; PC1 = VBUS_SENSE; HW-ID és HW_REV 16 sávos.

## 11. Rajz előtt / közben ellenőrizni
- [x] **STM32CubeMX-projekt** (2026-10-20, `hardware/cubemx/`): lábütközés nincs (CubeMX 6.18, mindhárom .ioc);
      a CubeMX-adatbázis szerint a COMP2 invertáló bemenete lehet a DAC1_CH1, a kimenete a TIM1 BKIN2 + TIM8 BKIN2.
      Egyetlen megkötés: a HDC3020 ALERT (PC2) nem kaphat EXTI-t (7. fejezet).
- [ ] A kvarc kiválasztása (CL) → a terhelőkondenzátorok értéke.
- [x] Az LM66200 (SOT-583-8) és a TPS2595 (DSG, ThermalVias) KiCad-footprintje a TI-rajzzal összevetve (2026-10-20) – egyezik.
- [ ] A lánc végén mért V_BUS az első prototípuson (a PC1-en) – ha 4,5 V alá esik: vastagabb kábel / rövidebb lánc.
