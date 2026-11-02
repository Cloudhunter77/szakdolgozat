# Modulmag – kapcsolási specifikáció (v1) – 2026-10-13, frissítve 2026-10-20 (D71), 2026-10-22 (D78, D79)

A KiCad-rajz alapja. A modulmag egy **hierarchikus lap**, amit a LED-, a relé- és a bemeneti modul ugyanabból a
fájlból használ. Lábszámok: ST hivatalos pin-adatai (STM32_open_pin_data, `STM32F303R(D-E)Tx.xml`); értékek: TI
adatlapok (ISO1042, TLV755P, ESD2CAN24-Q1, UCC27524, INA181), CUI P78E-1000, onsemi NCP1117, ST AN4206, STM32F3
HAL COMP-leírás. Független ellenőrzés után javítva (2026-10-13). **2026-10-14: a tápblokk P78E05 + NCP1117 lett
(D56, D57) – 2. fejezet; a vezérlő V_BUS-a 5,0 V (D59) – 5.5.** A busz másik oldala, a vezérlő: `VEZERLO-SPEC.md`.
Állapot: **javaslat** – a 11. fejezet pontjait rajz közben nézd át.

> **2026-10-20 – D71 (konzultáció után): központi 5 V, közös föld.** A modulmagon **nincs 24 V és nincs izoláció**: a
> logika a busz +5V-járól jár (AP2112K → 3,3 V), a CAN-transceiver **TCAN1044AV** (mint a vezérlőn), a busz GND-je
> a modul GND-je. A 2., 4., 5. és 6. fejezet ennek megfelelően átírva; a HW-ID 16 sávos (3.5). A 24 V-ot csak a
> LED- és a relémodul használja, a saját lapján (VIN_SENSE – D78 óta a PB1-en). Bekötési szabály: **a vezérlő és minden
> modul ugyanarról a (12–26 V-os) tápról jár, csillagpontosan**; busz-kábel AWG22.

> **2026-10-22 – D78, D79: MCU = STM32L433RCT3, transceiver = SN65HVD230 (mindkettő kézben).** Az L433 lábra kompatibilis
> az F303RET6-tal (azonos táp- és földlábak; 48 = VDDUSB → 3V3, 60 = PH3-BOOT0 a 10 k-s lehúzással), ugyanaz a bxCAN a
> PA11/PA12-n. Eltérések: **egy ADC** (a PB11–PB15 nem ADC-s → VIN_SENSE a **PB1**-re), **nincs TIM8** (a LED-modul CH4–CH6
> TIM15/TIM16-ra), a COMP2 nem invertáló bemenete a PA3 (I_SENSE oda), a debug-UART a PC4/PC5-ön **USART3**, 256 KB flash.
> A relé- és a bemeneti lap F303-mal is beültethető, a LED-lap csak L433-mal. A CAN-transceiver **SN65HVD230** (3,3 V,
> buszlábak −4…16 V – a TCAN1044AV ±58 V-jánál gyengébb, Balázs vállalja). A táp-LED (D3) a +5V-ról jár. A 3., 4. és
> 7. fejezet ennek megfelelően frissítve; a régi F303-as lábszámok azonosak.

> **2026-11-01 – D94: a busz-oldal leválasztható, a LED-modul leválasztva.** A konzultáción (10-28) kiderült: ha a LED-modul
> GND_IN vezetéke leesik, a szalag árama a buszon át (R293 → D5 → V_BUS) keres utat. Ezért a CAN-transceiver **CA-IS3052G**
> (izolált, lábkompatibilis a TI ISO1042BDWVR-rel), a busz-oldal (J2/J3, ESD2CAN24, D5, lezárás, fojtó) a **V_BUS / GND_BUS**-on
> van, a modul-oldal (+5V, GND) a modul saját lapján kapcsolódik hozzá: a **relé- és a bemeneti modulon 0 Ω-mal** (R100/R113,
> R300/R390 – nincs leválasztva), a **LED-modulon egy 1 W-os izolált DC-DC-vel** (U208 B0505S-1WR3; az R293 kikerült). A 4. és
> az 5. fejezet ennek megfelelően átírva.

## 0. Tartalom és változatok

| Blokk | Fő alkatrész | Fejezet |
|---|---|---|
| +5V (busz) → 3,3 V | AP2112K-3.3 | 2 |
| MCU + körítés | STM32L433RCT3 (LQFP64; tartalék: F303RET6), 8 MHz-es kvarc | 3 |
| CAN | SN65HVD230D (D79) | 4 |
| Busz | 2 × JST-XH, ESD2CAN24-Q1, 120 Ω + jumper, TVS | 5 |
| Debug | 1 × 7-es tüskesor (SWD + UART) | 3.6 |

- **Mindhárom modul a buszról kapja a logikai tápot (D71).** A LED- és a relémodul a terheléshez (szalag,
  tekercsek) saját 12–26 V-ot kap, a bemeneti modulon nincs 24 V.
- A korábbi A változat (P78E05 + NCP1117 a modulon, izolált ISO1042, `GND_BUS`) és a D66 opcionális buszos tápja
  (D6 + JP2) **elmarad**.

## 1. Netek

| Net | Honnan | Megjegyzés |
|---|---|---|
| `V_BUS` | J2/J3 1-es tű (a vezérlő V_BUS-a) | busz-oldal (D94): 4,5–5,2 V (a lánc végén kevesebb); a CAN-transceiver VCC2-je, a D5 TVS |
| `+5V` | a modul lapjáról (D94): a V_BUS 0 Ω-on át, a LED-modulon izolált DC-DC | modul-oldal: az LDO bemenete, a táp-LED, a VBUS_SENSE |
| `+3V3` | U5 | MCU, CAN-transceiver, VDDA (ferrit nélkül – D90) |
| `GND_BUS` | J2/J3 2-es tű | busz-oldal (D94): a transceiver GND2-je, az ESD2CAN24, a D5 |
| `GND` | a modul saját GND-je | a relén és a bemenetin 0 Ω-mal a `GND_BUS`-on, a LED-modulon leválasztva (D94) – a LED- és a relémodulon a 24 V-os GND is |
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

- Áramszükséglet a 3,3 V-on: STM32 ~20–30 mA + a CA-IS3052G logikai oldala (néhány mA) + LED-ek; a transceiver busz-oldali
  árama (adáskor ~70 mA) a V_BUS-ról közvetlenül jön (D94).
- A 3,3 V a lánc végén ~3,6 V-ig tart (0,25 V ejtés + tartalék); a D79 óta nincs 5 V-os fogyasztó, ami ennél szűkebb lenne.

## 3. STM32L433RCT3 és körítése (D78; az F303RET6 lábra azonos)

### 3.1 Táplálás (ST AN4206)
| Láb | Név | Bekötés |
|---|---|---|
| 1 | VBAT | `3V3` + 100 nF (nincs elem) |
| 19, 32, 48, 64 | VDD (L433-on a 48 = VDDUSB) | `3V3`, lábanként 100 nF + összesen 1 × 4,7 µF |
| 18, 31, 47, 63 | VSS | `GND` |
| 13 | VDDA (= VREF+ ezen a tokon) | `3V3`-ról közvetlenül (D90), + 1 µF + 10 nF a lábnál |
| 12 | VSSA | `GND` |

**Ferritgyöngy nincs (D90, konzulensi javaslat):** a gyöngy a hidegítő kerámiákkal csillapítatlan LC-kört alkot, a rezonanciáján
erősíti a zajt. Az ST szerint a VDDA nem lehet kisebb a VDD-nél, és nem jöhet fel később – a közvetlen bekötés ezt biztosan teljesíti.

### 3.2 Órajel
- **Y1:** 8 MHz-es kvarc (3225), PH0-OSC_IN (5) – PH1-OSC_OUT (6) (F303-on PF0/PF1). D85: 3TJ480000JWLAC – CL = 10 pF (→ C10/C11
  12 pF), ESR ≤ 120 Ω; a legolcsóbb 300 Ω-os kvarccal az L4 HSE erősítési tartaléka csak ~3 lenne (ST AN2867: ≥ 5).
- **C10, C11:** terhelőkondenzátorok = 2 × (CL − 3…5 pF szórt kapacitás) – a kiválasztott kvarc CL értékéből.
  Pl. CL = 10 pF → ~12 pF; CL = 8 pF → ~8 pF.
- Közvetlenül a lábak mellé, alatta csak GND, más jel ne fusson alatta.

### 3.3 Reset és boot
- **NRST (7):** 100 nF a GND-re + **R6 10 k felhúzás a +3V3-ra** (a gyenge, ~40 k-s belső mellé – D90); reset-gomb footprintje opcionális.
- **BOOT0 (60):** 10 kΩ a GND-re + egy tesztpad a `3V3`-hoz (tartalék; a programozás SWD-n megy). **A ROM-bootloader USART1-e az
  AN2606 szerint a PA9/PA10-en van, nem a J1 UART-ján (PC4/PC5)** – a J1-ről tehát csak SWD-vel programozható (D77).

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
- **HW_REV a PB0-n:** 3V3 – 10 kΩ – PB0 – R_bottom – GND, + 100 nF; ugyanaz a 16 sávos rendszer, mint a HW-ID-nél
  (3.5). **v1 = 1. sáv (715 Ω)**; 0 = hiba, 15 = a firmware-ből megadott (D71). **Az osztó a modul saját lapján van** (D89; a
  modulmag csak a `HW_REV` hierarchikus jelet adja ki, mint a HW-ID-nél) – LED: R295/R296/C295, relé: R115/R116/C107, bemeneti:
  R303/R304/C308; a NYÁK-on is a modulmag-blokkon kívül (LED: a HW-ID-osztó mellett; relé / bemeneti: a PB0-láb mellett).
- **J4** (2 × 5, 2,54 mm, DNP): 1 3V3 · 2 GND · 3 PA15 · 4 PB6 · 5 PB3 · 6 PB7 · 7 PB4 · 8 PB10 · 9 PB5 · 10 GND –
  SPI1 (PB3 SCK, PB4 MISO, PB5 MOSI, PA15 NSS), I²C1 alternatív lábai (PB6 SCL, PB7 SDA), PB10. A layoutnál dől el,
  hogy elfér-e.
- **Relémodul (a modul saját lapján):** J105 3,5 mm-es jack az SCT-013 lakatfogónak, R107/R108 10 k + C102 10 µF
  középfeszültség (1,65 V), R109 terhelő-ellenállás (csak áramkimenetes típushoz), R110 1 k + C103 10 nF → PA0. Minden DNP.

## 4. CAN – CA-IS3052G (U2), izolált (D94)
Chipanalog CA-IS3052G: izolált CAN-transceiver, 5 kVrms, buszlábak ±58 V, közös módus ±30 V, 1 Mbit/s (a bxCAN-nek elég),
SOIC8-WB (5,85 × 7,5 mm). **Lábkompatibilis a TI ISO1042BDWVR-rel** (az a drágább alternatíva ugyanarra a footprintre);
a CA-IS3050G-vel **nem** (ott a TXD és az RXD fel van cserélve). Mindhárom modulon ez van – a közös modulmag miatt; a relé-
és a bemeneti modulon a két oldal 0 Ω-mal össze van kötve, ott csak a robusztusabb buszlábak (±58 V) a haszon.

| Láb | Név | Bekötés |
|---|---|---|
| 1 | VCC1 | `+3V3` + C18 100 nF + C19 4,7 µF (modul-oldal) |
| 2 | TXD | **PA12** (45, CAN_TX) + **R1 10 kΩ felhúzás `3V3`-ra** (reset alatt recesszív busz) |
| 3 | RXD | **PA11** (44, CAN_RX) |
| 4 | GND1 | `GND` |
| 5 | GND2 | `GND_BUS` |
| 6 | CANL | `CAN_L_T` → JP3 (zárt) / L1 → `CAN_L` |
| 7 | CANH | `CAN_H_T` → JP2 (zárt) / L1 → `CAN_H` |
| 8 | VCC2 | `V_BUS` + C20 100 nF + C21 4,7 µF (busz-oldal, a GND_BUS-ra) |

- VCC1 2,5–5,5 V, **VCC2 4,5–5,5 V** – a V_BUS a lánc végén ~4,5 V-ig eshet (5.5), ez a határ; ha kevesebb, a modul VBUS_SENSE-e jelez.
- A korábbi SN65HVD230 (kézben 86 db) és az R12 (Rs) kikerült; az SN65HVD230 −4…16 V-os buszlábai helyett ±58 V.
- **Miért izolált (D94):** a LED-modulon a GND_IN szakadásakor a szalag árama a busz-GND-n, majd a D5-ön át a V_BUS-on
  keresett utat (a V_BUS ~7 V-ra is felmehetett). Leválasztva a LED-modul földje és a busz földje között nincs galvanikus
  kapcsolat: nincs hurokáram, a LED-ek PWM-zaja nem jut a buszra, és a LED-modul tápja bárhogy beköthető.

## 5. Busz

### 5.1 Csatlakozók – J2 (BUS_IN), J3 (BUS_OUT): JST-XH, 4 tű (B4B-XH-A)
| Tű | Jel |
|---|---|
| 1 | `V_BUS` (a vezérlő V_BUS-a) |
| 2 | `GND_BUS` (busz-oldal; a modul lapján a relén / bemenetin 0 Ω-mal a `GND`-re, a LED-modulon leválasztva – D94) |
| 3 | `CAN_L` |
| 4 | `CAN_H` |

J2 és J3 azonos tűi közvetlenül összekötve (átmenő busz). Az XH tűnként 3 A-t bír; a vezérlő 2 A-nél korlátoz.

**Busz-GND (D74 → D94):** a `GND_BUS` (XH 2-es tű) a busz-oldal földje: a transceiver GND2-je, az ESD2CAN24 és a D5 ehhez
fog. A modul lapján: **relémodul R113 = 0 Ω, bemeneti modul R390 = 0 Ω** a `GND`-re (+ R100 / R300 0 Ω a V_BUS → +5V-ra);
a **LED-modulon nincs kapcsolat** – a logika tápja az U208 izolált DC-DC-n át jön (C216 bemeneti, C217 kimeneti kondenzátor;
C218: EMC-kondenzátor helye a két föld között, DNP). **D95:** a relé- és a bemeneti modulon is ott a DC-DC helye (U100 / U300 +
kondenzátorok, DNP) – leválasztáshoz a két 0 Ω ki, a DC-DC be (a bemenetin így az érzékelőknek ~100 mA marad). A korábbi R293 (1 Ω) a hurokáramot csak csökkentette (~0,2 A), a GND_IN
szakadását nem kezelte – ezért kikerült.

**CAN-fojtó (D74):** a transceiver (CA-IS3052G) és a busz között **L1** közös módusú fojtó (DNP, pl. TDK ACT45B / ACM3225) és két zárt
forrasztható áthidaló (**JP2, JP3**) – mint a vezérlőn. Fojtó beültetésekor a JP2/JP3 átvágandó.

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
  végén kevés marad (D79 óta csak az AP2112K-nak kell ≥ ~3,6 V; a modul 4 V alatt jelezzen).
- **Bővítés áramtalanítva (D77):** egy feszültség alatt bedugott modul bemeneti kondenzátorai rövid V_BUS-letörést
  okoznak – a többi modul újraindulhat. A lánc bővítése előtt a vezérlőt áramtalanítani (vagy a GPIO20-szal a V_BUS-t KI).
- **Több táp (D77):** a D71-es „egy táp” szabály lazítható: több SELV-táp is mehet, ha a kimenetük lebegő (nincs a PE-re
  kötve), és a 0 V-ok egy ponton – a csillagpontban – vannak összekötve.

## 6. ~~A/B változat~~ – megszűnt (D71)
A korábbi A változat (saját 24 V → P78E05 → NCP1117, izolált ISO1042) és B változat (TLV75533 a V_BUS-ról) helyett
egyetlen kiépítés van: a 2. fejezet.

## 7. Lábkiosztás – minden modul egyszerre

A modulmag lábai minden modulon azonosak; a modulspecifikus lábak nem ütköznek velük. A bemeneti modul 16
bemenete 16 különböző lábszámon van → mindegyik saját EXTI-megszakítást kap. (Minden lábfunkciót az ST pin-adatai
alapján ellenőriztünk.) **D78 óta az ADC-csatornák az L433 szerint** (egy ADC: PC0–PC3 = IN1–4, PA0–PA7 = IN5–12,
PC4/PC5 = IN13/14, PB0/PB1 = IN15/16); a PB11–PB15 L433-on nem ADC-s.

| Láb | Port | Modulmag | LED-modul | Relémodul | Bemeneti modul |
|---|---|---|---|---|---|
| 2 | PC13 | STATUS-LED (nyelő) | | | |
| 5, 6 | PH0, PH1 (F303: PF0, PF1) | HSE 8 MHz | | | |
| 8 | PC0 | HW-ID (ADC1_IN1) | | | |
| 9 | PC1 | **VBUS_SENSE** (ADC1_IN2, D71) | | | |
| 10 | PC2 | | V_RAIL_SENSE (a főbiztosíték utáni 24 V, ADC1_IN3) | | HDC_ALERT |
| 11 | PC3 | | **T_SENSE** (MCP9701A, ADC1_IN4 – D78) | | |
| 14–16 | PA0–PA2 | | DS1–DS3 (drain-mérés, ADC1_IN5–7, D65) | | IN0–IN2 (ADC1_IN5–7) |
| 17 | PA3 | | **I_SENSE** (INA181 kimenet → ADC1_IN8 + COMP2_INP – D78) | | IN3 (ADC1_IN8) |
| 20 | PA4 | | **DAC1_OUT1 – foglalt** (a komparátor küszöbe; kívül nem bekötve, csak tesztpont) | | IN4 (ADC1_IN9) |
| 21, 22 | PA5, PA6 | | DS5, DS6 (drain-mérés, ADC1_IN10–11, D65) | | IN5, IN6 (ADC1_IN10–11) |
| 23 | PA7 | | **DS4** (drain-mérés, ADC1_IN12 – D78) | | IN7 (ADC1_IN12) |
| 24, 25 | PC4, PC5 | UART_TX/RX (L433: USART3, F303: USART1) | | | |
| 27 | PB1 | | **VIN_SENSE** (24 V az F201 előtt, ADC1_IN16 – D78) | **VIN_SENSE** (tekercs-táp, ADC1_IN16 – D78) | |
| 30 | PB11 | | | | IN11 (digitális) |
| 33 | PB12 | | DRV_EN (3 × UCC27524 EN) | REL1 | IN12 (digitális) |
| 34 | PB13 | | | REL2 | IN13 (digitális) |
| 35, 36 | PB14, PB15 | | **CH4, CH5 (TIM15_CH1/CH2 – D78)** | REL3, REL4 | IN14, IN15 (digitális) |
| 61 | PB8 | | **CH6 (TIM16_CH1 – D78)** | | I²C1 SCL (HDC3020) |
| 37–39 | PC6–PC8 | szabad (L433-on nincs rajtuk időzítő) | | | |
| 41–43 | PA8–PA10 | | CH1–CH3 (TIM1_CH1–3) | | IN8–IN10 |
| 44, 45 | PA11, PA12 | CAN_RX / CAN_TX | | | |
| 46, 49 | PA13, PA14 | SWDIO / SWCLK | | | |
| 60 | PH3-BOOT0 (F303: BOOT0) | 10 kΩ GND-re | | | |
| 62 | PB9 | | | | I²C1 SDA (HDC3020) |
| 26 | PB0 | **HW_REV** (NYÁK-revízió, ADC – D69) | | | |
| 29, 50, 55–59 | PB10, PA15, PB3–PB7 | **J4 bővítő** (DNP, D69) | | | |
| 14 | PA0 | | | **CT_SENSE** (SCT-013, DNP – D69) | |
| egyéb | | szabad → firmware-ben analóg mód | | | |

Megjegyzések:
- **LED-modul túláramvédelem (D53, D78):** I_SENSE a PA3-on a COMP2 nem invertáló bemenete. Az invertáló bemenet a
  **DAC1_OUT1** (PA4) – így a küszöb telepítésenként állítható (pl. a beállított max. áram 1,2-szerese, alapból
  ~22 A). Tartalék fix küszöbök: VREFINT ≈ 24 A, ¾ VREFINT ≈ 18 A, ½ VREFINT ≈ 12 A. A COMP2 kimenete belül a
  **TIM1, TIM15 és TIM16 break-bemenetére** (L433: a TIMx_OR2 BKCMP2E bitje; a CubeMX-adatbázis szerint mindhárom
  időzítőn elérhető – D78). A PB12-n lévő TIM1_BKIN / TIM15_BKIN lábfunkciót **nem szabad** bekapcsolni (ott a DRV_EN van).
  A TIM16-nak nincs slave-módja: a fázistolást (D24) az indítási sorrend adja (közös órajel, nem csúszik el). Áramerősítő: **INA181A2 (×50)**, alacsony oldali sönt
  (1 mΩ, a közös GND-visszatérőben – a közös módusú feszültség ~0 V, az INA181 26 V-os határa nem gond):
  20 A → 1,0 V az ADC-n, kb. 66 A-ig mér. A firmware a COMP2-t és a DAC-ot a DRV_EN bekapcsolása **előtt**
  állítja be.
- **DRV_EN:** a három UCC27524 hat EN-lába közösen a PB12-re, **1 kΩ lehúzással** (minden EN belsőleg ~200 kΩ-mal a
  12 V-ra húz, a hat párhuzamosan ~33 kΩ; 1 kΩ-mal ~0,35 V, biztosan a 0,8 V-os küszöb alatt – a korábbi 4,7 kΩ-mal
  ~1,5 V lett volna, D65) → boot alatt a driverek tiltva. A driverek
  IN-lábain belső lehúzás van, a lebegő PWM-láb is KI-t jelent.
- **Relék:** a ULN2803A bemenetein opcionális 100 kΩ lehúzás (boot alatti lebegés ellen).
- A bemeneti modulon L433-mal **8 bemenet ADC-képes (IN0–IN7)**, a többi csak digitális (F303-mal 13 volt) – a
  PA8–PA10 és a PB11–PB15 5 V-tűrő (FT); az ADC-s lábak ≤ 3,6 V-ot bírnak → 5 V-os jelhez osztó (D66). A HDC3020 ALERT-je a PC2-n.
- **EXTI-ütközés (CubeMX-adatbázis, 2026-10-20):** a PC2 az EXTI2 vonalon osztozna az IN2-vel (PA2) – egy EXTI-vonal
  egyszerre csak egy porté. Ezért a HDC3020 ALERT-je **sima bemenet, a firmware lekérdezi** (a riasztás úgyis lassú
  esemény). Más lábra tenni sem segítene: az IN0–IN15 mind a 16 EXTI-vonalat lefoglalja.

## 8. Layout-irányelvek
- A modulmag **mindhárom lapon ugyanott**, a felső vállnál (D50). KiCad-ben a layoutot is újrahasználható
  blokként kezelni.
- **Busz** a felső él mentén: J2, J3, JP1, R5, U3, D5, L1/JP2/JP3, a transceiver busz-oldala (5–8. láb) és a C20/C21 – ez a
  busz-oldal (V_BUS, GND_BUS). **A LED-modulon** körülötte minden rétegen ≥ 0,8 mm rés a modul GND-jétől (D94: a DRC-szabály
  ezt ellenőrzi), a GND_BUS-nak külön zóna; a határon csak az U2 és az U208 ül. A relé- és a bemeneti modulon rés nem kell.
- **U5 (AP2112K):** C2 és C3 közvetlenül a lábainál; SOT-23-5, kis disszipáció.
- **Kvarc:** a lábak mellett, GND-őrgyűrű, alatta semmi.
- **Hidegítés:** minden 100 nF a saját lábánál, a via a kondenzátor GND-oldalán.
- Debug-tüskesor a lap szélén; az állapot-LED-ek az előlap felőli szélen (fényvezető).

## 9. Darabjegyzék (egy modulmag, D71, D78, D79)
U5 AP2112K-3.3TRG1 (D80) · U2 CA-IS3052G (D94) · U3 ESD2CAN24-Q1 · STM32L433RCT3 · Y1 8 MHz · D5 SMF5.0A ·
D3/D4 zöld (522 nm, a +5V-ról)/piros LED · J1 1 × 7 tüskesor · J2/J3 B4B-XH-A · JP1 2 tűs + jumper · R6 10 k (NRST-felhúzás, D90) ·
kondenzátorok: 10 µF 16 V (0805, 2 db), 100 nF (≈ 10 db), 1 µF, 4,7 µF (3), 10 nF, 2 × C_kvarc · ellenállások:
10 k (több, ebből R3/R4 1 %), 1 k, 2,2 k, 120 Ω. (A HW-ID és a HW_REV osztója a modul saját lapján van, 3.5, 3.7 – D89.)

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
- **MCU és transceiver (2026-10-22) → D78, D79:** STM32L433RCT3 (kézben 75 db) az F303RET6 helyett, VIN_SENSE a PB1-en,
  LED-modul: CH4–CH6 TIM15/TIM16, I_SENSE a PA3-on; SN65HVD230 (kézben) a TCAN1044AV helyett; a táp-LED a +5V-ról.

## 11. Rajz előtt / közben ellenőrizni
- [ ] **STM32CubeMX-projekt L433-ra (D78, 2026-10-22):** a `gen/cubemx.py` újragenerálta – CubeMX-ben betölteni és
      megnézni (lábütközés; COMP2 → TIM1/TIM15/TIM16 break; DAC1 → COMP2 INM).
- [x] **STM32CubeMX-projekt** (F303, 2026-10-20, `hardware/cubemx/`): lábütközés nincs (CubeMX 6.18, mindhárom .ioc);
      a CubeMX-adatbázis szerint a COMP2 invertáló bemenete lehet a DAC1_CH1, a kimenete a TIM1 BKIN2 + TIM8 BKIN2 (régi, F303-ra).
      Egyetlen megkötés: a HDC3020 ALERT (PC2) nem kaphat EXTI-t (7. fejezet).
- [ ] A kvarc kiválasztása (CL) → a terhelőkondenzátorok értéke.
- [x] Az LM66200 (SOT-583-8) és a TPS2595 (DSG, ThermalVias) KiCad-footprintje a TI-rajzzal összevetve (2026-10-20) – egyezik.
- [ ] A lánc végén mért V_BUS az első prototípuson (a PC1-en) – ha 4,5 V alá esik: vastagabb kábel / rövidebb lánc.
