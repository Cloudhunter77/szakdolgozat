# Modulmag – kapcsolási specifikáció (v1) – 2026-10-13, frissítve 2026-10-14

A KiCad-rajz alapja. A modulmag egy **hierarchikus lap**, amit a LED-, a relé- és a bemeneti modul ugyanabból a
fájlból használ. Lábszámok: ST hivatalos pin-adatai (STM32_open_pin_data, `STM32F303R(D-E)Tx.xml`); értékek: TI
adatlapok (ISO1042, TLV755P, ESD2CAN24-Q1, UCC27524, INA181), CUI P78E-1000, onsemi NCP1117, ST AN4206, STM32F3
HAL COMP-leírás. Független ellenőrzés után javítva (2026-10-13). **2026-10-14: a tápblokk P78E05 + NCP1117 lett
(D56, D57) – 2. fejezet; a vezérlő V_BUS-a 5,0 V (D59) – 5.5.** A busz másik oldala, a vezérlő: `VEZERLO-SPEC.md`.
Állapot: **javaslat** – a 11. fejezet pontjait rajz közben nézd át.

## 0. Tartalom és változatok

| Blokk | Fő alkatrész | Fejezet |
|---|---|---|
| 24 V → 5 V → 3,3 V táp | P78E05-1000 + NCP1117ST33 | 2 |
| MCU + körítés | STM32F303RET6 (LQFP64), 8 MHz-es kvarc | 3 |
| Izolált CAN | ISO1042BDWVR | 4 |
| Busz-oldal | 2 × JST-XH, ESD2CAN24-Q1, 120 Ω + jumper, V_BUS-védelem | 5 |
| Debug | 1 × 7-es tüskesor (SWD + UART) | 3.6 |

- **Mindhárom modul (LED, relé, bemeneti) saját 24 V-ról jár:** minden beültetve, a busz galvanikusan
  leválasztva (D66 – a korábbi B változat elvetve).
- **Opcionális buszos táp (D66):** D6 (SS14 Schottky, `V_BUS_P` → `+5V`) és JP2 (forrasztható áthidalás,
  `GND_BUS` ↔ `GND`) – alapból **nincs beültetve / nyitva**. Beforrasztva a modul 24 V nélkül a V_BUS-ról jár
  (az 5 V ~4,5 V lesz, a 3,3 V az NCP1117-ről), de **izoláció nélkül**, és a vezérlő 382 mA-es korlátján osztozva;
  fejlesztéshez, asztali teszthez, vagy ha egy bemeneti modulhoz nem jut 24 V.

## 1. Netek és tartományok

| Tartomány | Netek | Megjegyzés |
|---|---|---|
| Logikai (modul) | `+24V_IN`, `+24V_P`, `5V`, `3V3`, `GND` | a modul saját tápja |
| Busz | `V_BUS`, `V_BUS_P`, `GND_BUS`, `CAN_H`, `CAN_L` | a vezérlőtől jön, a lánc közös referenciája |

A két tartomány között **csak az ISO1042** megy át (A változat).

`+24V_IN` = a modul 24 V-os bemenete. **A LED-modulon a 20 A-es főbiztosíték ELŐTT kell leágaztatni** (a saját
F1-gyel védve): így kiégett főbiztosítéknál is él a modul, és jelezni tudja (VIN_SENSE van, V_RAIL_SENSE nincs).

## 2. Tápblokk: 24 V → 5 V → 3,3 V (A változat) – P78E05 + NCP1117 (D56, D57)

Lánc: `+24V_IN` → F1 → D1 → R6 → (`+24V_P`) → D2 TVS, C12, C1 → U1 P78E05 → `5V` (C2) → U5 NCP1117 → `3V3` (C3).
A D1 a TVS **előtt** van: fordított polaritásnál a dióda zár, így a biztosíték nem ég ki.

**Miért így (D57):** a P78E05 bemenete legfeljebb **36 V** (abszolút maximum nincs megadva). A tüske-veszély a
modul 24 V-os betápján van (sorkapocs bedugása üzem közben, hosszú betápkábel) – a JST-láncon nincs 24 V (D28).
Csak kerámiával a kábel induktivitása LC-kört alkot, és bedugáskor a feszültség a 24 V közel kétszereséig
(~48 V) lenghet; a **C12 elkó** ESR-je ezt csillapítja. Az **R6** a C12-vel ~0,5 ms-os RC-szűrő, és korlátozza a
D2 áramát, így a TVS kis áramon, ~31–35 V-on fog (teljes impulzusáramnál ~45 V-on fogna). **A 24 V-os tápot ne
állítsd 26 V fölé.**

| Ref | Alkatrész | Érték / típus | Megjegyzés |
|---|---|---|---|
| F1 | SMD-biztosíték | 0,5 A, ≥ 32 V, gyors (1206) | a logikai ág saját védelme |
| D1 | Schottky | SS16 / B160 (60 V, 1 A, SMA) | fordított polaritás ellen; ~0,4 V esés |
| R6 | ellenállás | **0 Ω (D70)**; a footprint marad, szükség esetén 10 Ω, 1206, impulzusbíró (pl. Panasonic ERJ-P08) | 10 Ω-mal: esés üzemben ~0,25 V (~25 mA a 24 V-os oldalon); bedugáskor a C12 töltőárama ≤ 2,4 A (az F1-nek nem gond) |
| D2 | TVS | SMBJ28A | `+24V_P` → GND; Vbr 31,1–34,4 V |
| C12 | elektrolit – **kötelező** | 47 µF, 50 V, low-ESR, 105 °C | csillapítás bedugáskor / hosszú betápkábelnél; egyben a P78E05 adatlapja szerinti bemeneti kondenzátor (30 V felett 22 µF / 50 V kötelező) |
| C1 | kerámia | 10 µF, 50 V, X7R (1210) | közvetlenül a P78E05 1-es (VIN) és 2-es (GND) lába mellett (adatlap: 10 µF / 50 V) |
| U1 | DC/DC modul | **P78E05-1000** (CUI/Bel, SIP-3, furatszerelt) | 1 +VIN · 2 GND · 3 +VOUT (a 7805 lábkiosztása); 8–36 V be, 5 V (±1,5 % tip., ±3 % max.), 1 A, 93 % (min. Vin, teljes terhelés), üresjárás ~0,3 mA, 75 mVp-p, rövidzár-védett; 11,6 × 8,0 × 10,4 mm |
| C2 | kerámia | 22 µF, 10 V, X7R (1206) | `5V` kimenet (adatlap: 22 µF / 10 V); egyben az NCP1117 bemeneti kondenzátora; a P78E05 max. kapacitív terhelése 680 µF |
| U5 | LDO | **NCP1117ST33T3G** (SOT-223) | 1 GND · 2 OUT · 3 IN · fül = OUT; bemenet abs. max. 20 V; ejtés 100 mA-en max. 1,1 V; disszipáció (5 − 3,3) V × ~0,1 A ≈ 0,17 W |
| C3 | kimeneti | 10 µF tantál (3216-18, ESR 0,1–2 Ω) **vagy** 22 µF kerámia + 0,1 Ω soros ellenállás | az NCP1117 stabilitásához min. 4,7 µF, ESR ~33 mΩ–2,2 Ω kell – egy tiszta kerámia ESR-je ez alatt lehet |
| R3, R4, C9 | osztó | 150 kΩ / 10 kΩ, 100 nF | `+24V_P` → **PC1** (VIN_SENSE): 24 V → 1,5 V; 3,3 V-os végkitérés ≈ 53 V. A forrásimpedancia ~9,4 kΩ → hosszú ADC-mintavételi idő; a firmware hozzáadja a D1 (~0,4 V) és az R6 (~0,25 V) esését |

- Áramszükséglet: STM32 ~40 mA + ISO1042 1. oldal ≤ 3,5 mA + LED-ek → < 100 mA a `3V3`-on; a P78E05 1 A-t ad.
- Az `5V` sín a modul lapján elérhető (pl. egy későbbi WS2812C állapot-LED-hez, 74HCT14-es szintillesztéssel –
  nem része a v1-nek).
- A korábbi LMR36006BRNXR-es buck-blokk (L1, BOOT-, VCC-, FB-alkatrészek) **elmarad** (D56). A vezérlőn a V_BUS
  szintén P78E05-ről jön (D59), a 3,3 V-hoz ott LMR36015 buck kell – `VEZERLO-SPEC.md`.

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

### 3.5 Hardverazonosító (HW-ID)
3V3 – R_top – **PC0** (8) – R_bottom – GND, + 100 nF a PC0-n. **Az osztó és a 100 nF a modul saját lapján van**
(a modulmag csak a `HW_ID` hierarchikus jelet adja ki), mert modulonként más az értéke. A firmware 8 sávra osztja,
**kerekítve**: `sáv = (ADC + 256) / 512` (12 bites ADC, egész osztás) – így a névleges értékek a sávok közepére
esnek (k × 0,4125 V), nem a határukra:

| Modul | R_top | R_bottom | Feszültség | Sáv |
|---|---|---|---|---|
| LED | 10 kΩ | 3,3 kΩ | 0,82 V | 2 |
| Relé | 10 kΩ | 10 kΩ | 1,65 V | 4 |
| Bemeneti | 3,3 kΩ | 10 kΩ | 2,48 V | 6 |
| (tartalék) | – | – | 0, 1, 3, 5, 7 | későbbi modulok / revíziók |

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
- **HW_REV a PB0-n:** 3V3 – R10 (DNP) – PB0 – R11 10 kΩ – GND, + C20 100 nF. v1: csak az R11 → 0 V = 0. sáv; a későbbi
  revíziók a HW-ID sávjai (3.5) szerint ültetik be az R10/R11-et, így ugyanaz a firmware felismeri a NYÁK-változatot.
- **J4** (2 × 5, 2,54 mm, DNP): 1 3V3 · 2 GND · 3 PA15 · 4 PB6 · 5 PB3 · 6 PB7 · 7 PB4 · 8 PB10 · 9 PB5 · 10 GND –
  SPI1 (PB3 SCK, PB4 MISO, PB5 MOSI, PA15 NSS), I²C1 alternatív lábai (PB6 SCL, PB7 SDA), PB10. A layoutnál dől el,
  hogy elfér-e.
- **Relémodul (a modul saját lapján):** J105 3,5 mm-es jack az SCT-013 lakatfogónak, R107/R108 10 k + C102 10 µF
  középfeszültség (1,65 V), R109 terhelő-ellenállás (csak áramkimenetes típushoz), R110 1 k + C103 10 nF → PA0. Minden DNP.

## 4. Izolált CAN – ISO1042BDWVR (U2)

| Láb | Név | Bekötés |
|---|---|---|
| 1 | VCC1 | `3V3` + 100 nF |
| 2 | TXD | **PA12** (45, CAN_TX) + **10 kΩ felhúzás `3V3`-ra** (reset alatt lebegő láb → recesszív busz; az adatlap kéri) |
| 3 | RXD | **PA11** (44, CAN_RX) |
| 4 | GND1 | `GND` |
| 5 | GND2 | `GND_BUS` |
| 6 | CANL | `CAN_L` |
| 7 | CANH | `CAN_H` |
| 8 | VCC2 | `V_BUS_P` + 100 nF + 4,7 µF (`GND_BUS`-ra), a felső rétegen, via nélkül |

- Áramfelvétel (VCC2 = 5 V, 60 Ω-os terhelés): recesszív ~2,8 mA, domináns 43 mA tipikus / **73,4 mA max.**
- VCC2 működési tartomány 4,5–5,5 V (abszolút max. 6 V); alulfeszültségnél 3,8–4,25 V között lekapcsol.
- Az izolációs rés a tok alatt **minden rétegen** rézmentes (a DWV footprint ~9 mm-es rést ad).
- A TXD domináns-időkorlátja (min. 1,2 ms) miatt a legkisebb bitráta ~9,2 kbit/s – a tervezett 125–1000 kbit/s-nál
  ez nem gond.

## 5. Busz-oldal (`GND_BUS`-tartomány)

### 5.1 Csatlakozók – J2 (BUS_IN), J3 (BUS_OUT): JST-XH, 4 tű (B4B-XH-A)
| Tű | Jel |
|---|---|
| 1 | `V_BUS` |
| 2 | `GND_BUS` |
| 3 | `CAN_L` |
| 4 | `CAN_H` |

J2 és J3 azonos tűi közvetlenül összekötve (átmenő busz); a modul a `V_BUS`-t közvetlenül használja (`V_BUS_P`,
polyfuse nincs – D55).

### 5.2 V_BUS-védelem
- **Nincs PTC (D55, 2026-10-14):** a zárlatvédelmet a vezérlő TPS2553-a (áramkorlátos kapcsoló, 382 mA felett
  korlátoz) adja – egy 0,5 A-es PTC ennél később oldana ki, csak feszültséget ejtene.
- **D5:** TVS, 5 V standoff (SMF5.0A vagy SMBJ5.0A): `V_BUS_P` → `GND_BUS`, a J2/J3 mellett – **ESD és hot-plug
  tüskék ellen** (feszültség alatt bedugott XH-kábel).
- **24 V elleni védelem nincs (D55):** a láncon nincs 24 V (D28), az XH és a PH nem dugható össze. Az ISO1042
  VCC2-je (és a B változatban a TLV75533) abszolút maximuma 6 V – egy félredugott 24 V tönkretenné őket.

### 5.3 ESD – U3: ESD2CAN24-Q1 (SOT-23)
1 → `CAN_L` · 2 → `CAN_H` · 3 → `GND_BUS` (az 1 és 2 felcserélhető). A J2/J3 közvetlen közelében, rövid, vastag
GND_BUS-bekötéssel.

### 5.4 Lezárás – JP1 + R5 (D49, D52)
`CAN_H` → **JP1** (2 tűs, 2,54 mm, jumper) → **R5 120 Ω** (0805) → `CAN_L`.
Jumper bedugva = lezárva – **csak a lánc két végén** (a vezérlőn és az utolsó modulon).
**Miért nem osztott lezárás:** egyetlen jumperrel nem lehet tisztán kikapcsolni – nyitott állásban a 60 Ω + 4,7 nF
a CAN_L-en maradna minden lezáratlan modulon (aszimmetrikus terhelés). 0,5 m-es buszon a sima 120 Ω tökéletes.

### 5.5 V_BUS-mérleg (a vezérlő oldalára, D64)
Az ISO1042 busz-oldala (VCC2) recesszív állapotban **≤ 4,1 mA**-t vesz fel; a **≤ 73 mA** csak annál a modulnál
folyik, amelyik éppen ad (a 60 Ω-os lezárást hajtja – az ACK-bitnél többen is, de ugyanazon a lezáráson
osztozva, egy bitideig). Ezért:

> I(V_BUS) ≈ **73 mA** (az adó) + **4 mA × modul** (+ a buszos tápra kapcsolt modulok teljes fogyasztása, D66)

A vezérlő TPS2553 áramkorlátja **382 / 425 / 476 mA** (61,9 kΩ, `VEZERLO-SPEC.md` 2.4) → több tucat modul is
belefér; előbb a CAN csomópontszáma és a lánc hossza a korlát. Buszos tápra kapcsolt modulonként ~80–150 mA
(MCU + érzékelők) jön hozzá – ha ilyenből több kell, az R12 csökkentésével emelhető. A vezérlő V_BUS-a **5,0 V ± 3 %** (P78E05, D59): a TPS2553 és a kábel
után legrosszabb esetben **~4,75 V** marad a modulon, az ISO1042-nek 4,5 V kell.

## 6. ~~B változat: táplálás a V_BUS-ról~~ – elvetve (D66): a bemeneti modul is saját 24 V-ról jár; 24 V nélkül a D6 + JP2 buszos táp (1. fejezet)
- A 2. fejezet alkatrészei **nincsenek beültetve**.
- **U4:** TLV75533PDBVR (500 mA LDO, SOT-23-5): 1 IN ← `V_BUS_P` · 2 GND · 3 EN → IN-re · 4 NC · 5 OUT → `3V3`.
  IN: 1 µF, OUT: 2,2 µF. Ejtés 500 mA-en max. ~0,24 V – bőven elég. Bemenet abszolút max. 6 V (lásd 5.2).
- **R0 (0 Ω):** `GND_BUS` ↔ `GND` a modul lapján (itt nincs leválasztás – a busz-tartomány maga a modul).
- Fogyasztás: STM32 + ISO1042 + HDC3020 + érzékelők ≈ 150 mA (ISO1042 dominánsan 73 mA-ig).

## 7. Lábkiosztás – minden modul egyszerre

A modulmag lábai minden modulon azonosak; a modulspecifikus lábak nem ütköznek velük. A bemeneti modul 16
bemenete 16 különböző lábszámon van → mindegyik saját EXTI-megszakítást kap. (Minden lábfunkciót az ST pin-adatai
alapján ellenőriztünk.)

| Láb | Port | Modulmag | LED-modul | Relémodul | Bemeneti modul |
|---|---|---|---|---|---|
| 2 | PC13 | STATUS-LED (nyelő) | | | |
| 5, 6 | PF0, PF1 | HSE 8 MHz | | | |
| 8 | PC0 | HW-ID (ADC1/2_IN6) | | | |
| 9 | PC1 | VIN_SENSE (ADC1/2_IN7) | (a főbiztosíték előtt) | | |
| 10 | PC2 | | V_RAIL_SENSE (a főbiztosíték utáni 24 V, ADC1/2_IN8) | | |
| 11 | PC3 | | NTC (ADC1/2_IN9) | | |
| 14–17 | PA0–PA3 | | DS1–DS4 (drain-mérés, ADC1_IN1–4, D65) | | IN0–IN3 (ADC1_IN1–4) |
| 20 | PA4 | | **DAC1_OUT1 – foglalt** (a komparátor küszöbe; kívül nem bekötve, csak tesztpont) | | IN4 (ADC2_IN1) |
| 21, 22 | PA5, PA6 | | DS5, DS6 (drain-mérés, ADC2_IN2–3, D65) | | IN5, IN6 (ADC2_IN2–3) |
| 23 | PA7 | | **I_SENSE** (INA181 kimenet → ADC2_IN4 + COMP2_INP) | | IN7 (ADC2_IN4) |
| 24, 25 | PC4, PC5 | UART_TX/RX (USART1) | | | |
| 30 | PB11 | | | | IN11 (ADC1/2_IN14) |
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
- **Busz-tartomány** a felső él mentén: J2, J3, JP1, R5, U3, D5, az ISO1042 2. oldala és a VCC2-kondenzátorok.
  A tartományhatár rézmentes sávja ≥ 2–3 mm (funkcionális szigetelés, mindkét oldal törpefeszültségű); az ISO1042
  alatt a teljes rés, **minden rétegen**.
- A 24 V-os betáp-sorkapocs is a felső vállon van, de a logikai tartományban → ≥ 3 mm a busz-tartománytól.
- **P78E05 + NCP1117:** a C1 és a C12 közvetlenül a P78E05 VIN–GND lábainál, a C2 a kimenetén; a P78E05
  furatszerelt (a reflow után kézzel forrasztva), 10,4 mm magas – a C12 elkóval együtt a DIN-ház vállmagassága
  alá kell férnie (szükség esetén fekvő elkó). Az NCP1117 füle (OUT) alatt ~1 cm² réz a hűtéshez.
- **Kvarc:** a lábak mellett, GND-őrgyűrű, alatta semmi.
- **Hidegítés:** minden 100 nF a saját lábánál, a via a kondenzátor GND-oldalán.
- Debug-tüskesor a lap szélén; az állapot-LED-ek az előlap felőli szélen (fényvezető).

## 9. Darabjegyzék (A változat, egy modulmag)
U1 P78E05-1000 · U5 NCP1117ST33T3G · U2 ISO1042BDWVR · U3 ESD2CAN24-Q1 · STM32F303RET6 · Y1 8 MHz · F1 0,5 A ·
D1 SS16 · D2 SMBJ28A · D5 SMF5.0A · D3/D4 piros/zöld LED · J1 1 × 7 tüskesor ·
J2/J3 B4B-XH-A · JP1 2 tűs + jumper · FB1 ferrit (≤ 0,1 Ω) vagy 0 Ω · kondenzátorok: 10 µF 50 V (1210), 47 µF
50 V elektrolit (kötelező), 22 µF 10 V (1206), 10 µF tantál (3216) – vagy 22 µF kerámia + 0,1 Ω –, 100 nF
(≈ 9 db), 1 µF (1), 4,7 µF (2), 10 nF, 2 × C_kvarc · ellenállások: 150 k, 10 k (több), 10 Ω (1206, impulzusbíró,
opc.), 1 k, 2,2 k, 120 Ω. (A HW-ID osztó a modul saját lapján van, 3.5.)

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

## 11. Rajz előtt / közben ellenőrizni
- [x] **STM32CubeMX-projekt** (2026-10-20, `hardware/cubemx/`): lábütközés nincs (CubeMX 6.18, mindhárom .ioc);
      a CubeMX-adatbázis szerint a COMP2 invertáló bemenete lehet a DAC1_CH1, a kimenete a TIM1 BKIN2 + TIM8 BKIN2.
      Egyetlen megkötés: a HDC3020 ALERT (PC2) nem kaphat EXTI-t (7. fejezet).
- [ ] A kvarc kiválasztása (CL) → a terhelőkondenzátorok értéke.
- [ ] SMD-biztosíték (F1: ≥ 32 V!) konkrét típusa.
- [ ] KiCad-footprintek: ISO1042 **DWV** (7,5 mm széles test, nem sima SOIC-8) – a TI EDA-modelljéből; **P78E05:**
      SIP-3, 2,54 mm-es lábtáv (a test más, mint a TO-220-as 7805-é – a CUI/Bel 3D-modelljéből); NCP1117: SOT-223.
- [ ] A P78E05 (10,4 mm) és a C12 elkó magassága a választott DIN-ház vállmagasságához (D50).
- [ ] Az NCP1117 kimeneti kondenzátora: tantál, vagy kerámia + 0,1 Ω (ESR ~33 mΩ–2,2 Ω).
- [ ] R6: beültetve (10 Ω) vagy 0 Ω – a VIN_SENSE-korrekció a firmware-ben ehhez igazodik.
