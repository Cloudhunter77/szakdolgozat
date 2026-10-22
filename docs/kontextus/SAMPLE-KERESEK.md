# Sample-kérések – 2026-10-13, frissítve 2026-10-14

Az aktuális architektúra (D27–D61) alapján, a 2026-10-10-i lista helyett. Mennyiség: védésre vezérlő +
3 modul (LED 6 csatornás, relé, általános bemeneti modul 16 bemenettel) + tartalék. **Min.** = ami a
prototípushoz kell, **Kérni** = ennyit érdemes kérni (ha a program kevesebbet enged, a minimum a fontos).
A pontos alkatrészek: `MODULMAG-SPEC.md`, `VEZERLO-SPEC.md`.

> **2026-10-23 – a rendeléshez ez a mérvadó (D85):** `hardware/bom/beszerzes.csv` (a `hardware/gen/beszerzes.py` állítja elő a
> BOM-ból: tételenként forrás – Hestore-kód, ár, készlet / Mouser-TME típusszám / TI-rendelés / kézben). Összefoglaló a
> fájl végén („Beszerzés 2026-10-22”). A lenti listák a sample-kérések története.

**2026-10-14:** a modulmag tápja **P78E05-1000 + NCP1117ST33** lett (mindkettő kézben, D56), és a vezérlő V_BUS-át is
a **P78E05** adja (D59) → **az LMR36006 sehol nem kell**; a vezérlő CAN transceivere **TCAN1044AVDRQ1** (D60) a TCAN330
helyett.

Tippek: egyetemi e-mail, a szakdolgozat címe a kérelemben, alkatrészenként 2–5 db, ugyanaz a funkció két
gyártótól. **Most kell kérni:** a döntés (TI) kb. 5 munkanap, a szállítás 1–2 hét; a beültetés a NYÁK
megérkezése után (≈ november közepe) lesz.

## TI – 1. prioritás (hozzáférést kell kérni céges/egyetemi e-maillel)

**Állapot (2026-10-19): a TI-rendelés leadva.** Előzmény: a hozzáférési kérelem elküldve (myTI → Contact support → Orders & payments → Sample program;
BME, TMIT, balazs.csanyi07@edu.bme.hu; a lenti 11 típus, 10 db/típus). A TI GYIK szerint hallgatóknak általában nem
adnak mintát – ha elutasítják, 10-22-én megrendelni (TI-boltból vagy TME/Mouser, ~60–70 USD).

| Alkatrész | Mire | Hova | Min. | Kérni | Ha nem jön |
|---|---|---|---|---|---|
| **ISO1042BDWVR** | izolált CAN transceiver (D33) | modulmag | 3 | 5 | breakout a padekre, izoláció nélkül (D36) |
| **TCAN1044AVDRQ1** (SOIC-8) | nem izolált CAN transceiver, ±58 V (D60) | vezérlő | 1 | 2 | MCP2562FD (Microchip) – lábról lábra azonos; vagy TCAN330 / SN65HVD230 a jumperek átforrasztásával |
| **LMR36015BRNXR** (1 MHz) | 60 V-os buck, 1,5 A (VQFN-HR 2 × 3 mm – reflow) | vezérlő 3,3 V (C6 + W5500) | 1 | 2 | **megvenni** – nincs tartalék |
| **UCC27524** | kétcsatornás gate driver (D17) – 6 csatornához 3 db | LED-modul | 3 | 4 | TC4427 (Microchip) vagy megvenni |
| **INA181A2** (×50, SOT-23-6) | össz-áram mérése az 1 mΩ-os söntön + hardveres túláramvédelem (D47, D53 – ×50, hogy 20 A felett is legyen tartomány) | LED-modul | 1 | 2 | megvenni (olcsó) |
| **ESD2CAN24-Q1** (SOT-23) | CAN ESD-védelem (CANH + CANL) | vezérlő + modulok | 4 | 5 | elhagyható a prototípusban |
| **TPD4E05U06** (USON 2,5 × 1 mm) | 4 csatornás ESD-védelem – 16 bemenethez 4 db | bemeneti modul | 4 | 5 | bármilyen 4 csatornás 5 V-os ESD-tömb |
| **TPS2553DBVR** | áramkorlátos kapcsoló a V_BUS-ra (61,9 kΩ → 382/425/476 mA) | vezérlő | 1 | 2 | polyfuse |
| **ULN2803A** | relémeghajtó (kimaradt az AliExpress-rendelésből) | relémodul | 1 | 2 | megvenni (olcsó) |
| **HDC3020** | hőmérséklet + páratartalom, I²C (WSON 2,5 × 2,5 mm) | bemeneti modul | 1 | 2 | bármilyen I²C-s T/RH szenzor |
| ~~**TLV75533PDBVR**~~ (D66: már nem kell, a TI-kérelemben benne maradt) (TLV755P, 3,3 V, SOT-23-5) | 500 mA-es LDO – a bemeneti modul a V_BUS-ról jár (B változat) | bemeneti modul | 1 | 2 | bármilyen 3,3 V-os LDO SOT-23-5-ben; végszükségben a kézben lévő NCP1117ST33 (SOT-223 – más footprint, ejtés ≤ 1,1 V, a V_BUS-ról még elég) |
| **LM74700QDBVRQ1** (LM74700-Q1, SOT-23-6) | ideális dióda-vezérlő – fordított polaritás elleni védelem a 20 A-es ágon (D65) | LED-modul | 1 | 2 | áthidalás dróttal (a Q201 S–D padjei között) **– D78 óta nem kell** (N-FET a GND-ágban) |

A **TPS2660** (eFuse) nem kell: a V_BUS-on nincs 24 V elleni védelem (D55, 2026-10-14).

## onsemi (MyON fiók, darabszám-korlát lehet)

| Alkatrész | Mire | Hova | Min. | Kérni |
|---|---|---|---|---|
| **NTD5C648NL** (60 V, 4,1 mΩ, DPAK) | LED-csatorna FET – az IPD053N06N helyett, mert az Infineon nem ad sample-t | LED-modul (6 csatorna) | 6 | 8 |
| Schottky, 3 A, 60 V (**B360B**, SMB) | szabadonfutó dióda drain → a blokk +24 V-ja (D65) | LED-modul | 6 | 8 |
| **NTMFS5C604NL** (60 V, ~1,2 mΩ, SO-8FL) | az ideális dióda FET-je a 20 A-es ágon (Q201, D65) | LED-modul | 1 | 2 |
| **MC78L12** (SOIC-8) | 12 V a gate drivereknek | LED-modul | 1 | 2 |
| TVS, 28 V standoff (**SMBJ28A**) | 24 V-os bemenet (modulmag D2; vezérlő D2, D7) | modulok + vezérlő | 5 | 6 |
| TVS, 5 V standoff (**SMF5.0A / SMBJ5.0A**) | V_BUS (D28; modulmag D5, vezérlő D4) | modulok + vezérlő | 4 | 5 |
| Schottky, 1 A, 60 V (**SS16 / B160**, SMA) | fordított polaritás (modulmag D1; vezérlő D1, D8) | modulok + vezérlő | 5 | 6 |
| Schottky, 3 A, 60 V (**B360 / SS36**) | a vezérlő USB-ága (D3) – 60 V-os kell, kis eséssel | vezérlő | 1 | 2 |

A kézben lévő FET-ek (IRFP064N, FDP2532) tartaléknak jók, ha a NYÁK-on van helyük – nagyobb tokok. Az **IRFR1205**
(kézben, DPAK, 55 V, 27 mΩ) ugyanarra a footprintre mehet, de 10 A-en ~2,7 W → nagy rézfelület kell.

## Würth Elektronik (kapcsolatfelvételi űrlap, szakdolgozathoz ingyenes)
- Tároló tekercs a vezérlő LMR36015-jéhez: **6,8 µH, Isat ≥ 2,1 A** (ideálisan ≥ 2,8 A), árnyékolt, ~5 × 5 mm
  (WE-MAPI / WE-LHMI) – 2 db (a modulokon nincs buck, D56)
- Elektrolit kondenzátor, 470 µF, ≥ 35 V (a LED-modul 24 V-jára; 63 V-os, ha a 48 V-os változatra is gondolsz) – 2 db;
  + **47 µF / 50 V-os, low-ESR elkó** a modulmag (C12) és a vezérlő (C1) bemenetére – **kötelező** (D57, D59),
  laponként 1 (+ tartalék)
- TVS-diódák (28 V, 5 V), ha az onsemi nem ad
- Push-in NYÁK-sorkapocs (WR-TBL), ha a Phoenix nem ad
- Ferrit és CAN közös módusú fojtó most nem kell (D24: csak footprint)

## Coilcraft (diákok „észszerű mennyiséget” kérhetnek)
- Tároló tekercs a vezérlő buckjához (pl. XAL5030-sorozat, 6,8 µH, Isat ≥ 2,1 A), ha a Würth nem ad – 2 db

## Phoenix Contact (ingyenes, ingyenes szállítással)
Push-in NYÁK-sorkapcsok (D30) – a pontos áramterhelhetőséget a katalóguslapon ellenőrizni; a DIN-ház vállai
alá férő magasságút (D50):
- LED-modul (D43): 2 pólusú betáp **2,5 mm²-hez, ≥ 20 A** + **3 db 3 pólusú kimenet** ([+24 V, CHa, CHb],
  10 A/csatorna; az iker érvéghüvelyt fogadja-e – ellenőrizni)
- Relémodul: 4 relé kimenete (≥ 250 V, ≥ 16 A, **4 × 2 pólus, COM + NO**, D62) + betáp
- Többi modul és vezérlő: 24 V-os betáp (kis áram)

## Microchip (második forrás, opcionális; a gmail-t elutasíthatja)
- **MCP2562FD** – nem izolált CAN transceiver (5 V + VIO, ±58 V), a TCAN1044AV helyére lábról lábra beültethető – 2 db
- **TC4427** – gate driver tartalék a UCC27524 helyett – 3 db

## Kézben – nem kell kérni (2026-10-14, `beszelgetesek/2026-10-14-alkatreszkeszlet-p78e05.md`)
- **Schrack RTD14024** (~50 db) – 16 A-es, 24 V DC-s relé a relémodulra (D62)
- **P78E05-1000** (~200 db) – a modulmag 24 V → 5 V-ja (D56) és a vezérlő V_BUS-a (D59)
- **NCP1117ST33T3G** (tekercs) – 5 V → 3,3 V (D56); LM3940 3,3 V (19 db) tartaléknak
- **74HCT14D** (36 db) – a vezérlő RGB LED-jének szintillesztője (U9); **WS2812C-2020** – a vezérlő RGB LED-je lehet
- LM2904 / LM2902, IRFR1205, ACS758LCB-100B, LM2576S – tartaléknak / későbbre

## D71 (2026-10-20) – új tétel: vásárlás
A konzultáció után a táp központi lett (D71) → új alkatrészek, egyik sincs a 10-19-i TI-kérésben:
- **DigiKey/Mouser (TI):** LMR33630ADDA (5 V-os buck, vezérlő) · TPS259531DSGR (eFuse, vezérlő) · LM66200DRLR
  (ideális dióda, vezérlő) · +3 db TCAN1044AVDRQ1 (a modulokra, az ISO1042 helyett) – tartalékkal együtt
- **Kínai kör:** AP2112K-3.3TRG1 (LDO, modulonként 2 – modulmag + a bemeneti modul érzékelősínje) · 8,2 µH-s
  árnyékolt tekercs (Isat ≥ 3,5 A, pl. SRN6045TA-8R2M) · B360 (SMC) a vezérlő D1-ére · 2 A-es 1206 biztosíték
- **Csak 12 V-os relémodulhoz:** 12 V-os tekercsű Schrack relé (RTD14012), 4 db
- Ha az ISO1042 minta mégis megjön: tartalék egy későbbi izolált változathoz.

## D73 (2026-10-21) – DIN-ház
- **TME:** Gainta **D4MG** × 3 (vezérlő, LED-, relémodul) + 1 tartalék, ~4,4 €/db; a bemeneti modulhoz a **6 modulos** Gainta (86,5 × 103 mm-es NYÁK) – a pontos típust a TME-n kikeresni

## D74–D77 (2026-10-21) – szakértői átnézés után
- Vezérlő: **SMBJ6.0A** (SMB) × 1 a +5V_BUCK-ra, **SMF5.0A** (SOD-123F) × 1 a VUSB-re
- Modulok: **1 Ω, 1206** × 1 (LED-modul, busz-GND), **0 Ω, 1206** × 2 (relé, bemeneti); a CAN-fojtó (pl. TDK ACT45B-510) csak
  akkor, ha a mérés indokolja (DNP)
- Bemeneti modul: a soros ellenállások 10 k-sak lettek → 0603 10 k bővebben (+16 db)
- Relémodul: SCT-013-jack, ha később kell: CUI **SJ1-3513N** (a 3523N helyett)

## Már nem kell
- **ISO1042BDWVR** a v1-hez (D71: közös föld) · a modulokon a **P78E05** és az **NCP1117** (D71) · TPS2553 (D71)
- THVD1450, ADM2587E, LTC2862 – RS-485-höz kellettek, a CAN-busz kiváltotta.
- ADE7953 (ADI) – a fogyasztásmérés v2 (D37).
- INA181A3 (×100) – helyette INA181A2 (×50), D53.
- **LMR36006** és a tekercsei – a modulokon (D56) és a vezérlőn (D59) is a P78E05 váltja ki.
- TCAN330 – a vezérlőn a TCAN1044AV váltja ki (D60); ha mégis jön, jumperrel beültethető tartalék.

## Nem sample – vásárolni kell
- ESP32-C6-WROOM-1-N16 a vezérlőre (vagy átmenetileg a DevKit); fém szekrénybe a WROOM-1U (U.FL) + külső antenna
- **Ethernet (D45):** W5500 (LQFP48), RJ45 beépített trafóval – **MagJack, külön TCT/RCT lábbal** (WIZnet:
  CETUS J1B1211CCD; olcsóbb: HR911105A – a lábkiosztását ellenőrizni), 25 MHz-es kvarc, ferrit 120 Ω @ 100 MHz
- **USB-C (vezérlő):** 16 tűs USB 2.0-s Type-C aljzat (pl. HRO TYPE-C-31-M-12 / GCT USB4105), **USBLC6-2SC6**,
  BAT54 (V_BUS-tiltás), 2 db SMD nyomógomb (RESET, BOOT)
- **RGB LED (vezérlő):** WS2812B-V5 (ha nem a kézben lévő WS2812C-2020 + 74HCT14)
- **JST-XH** (busz, D38): 4 tűs álló aljzatok (B4B-XH-A) és dugók – laponként 2 (a vezérlőn is, D58) + kábelek
- **JST-PH** (érzékelők, D51 javaslat): **3 tűs aljzatok (16 db)** + dugók
- 2,54 mm-es jumperek és 2 tűs tüskesorok + **120 Ω-os ellenállás** laponként (CAN-lezárás, D49, D52 – sima 120 Ω)
- **AH1911** – a 6 fiókos komódhoz legalább 6 kell, 5 van → legalább 5 db pótlás (+ mágnesek)
- **Littelfuse NANO² 451/453 (2410)** SMD biztosíték, pl. 0451010.MRL (10 A) – a LED-modul 3 kimeneti blokkjára (D65), + néhány
  kisebb érték (5 A, 7 A) a szalagokhoz
- Mini lapos (autós) biztosíték NYÁK-foglalattal + 20 A-es biztosíték (LED-modul)
- **SMD-biztosítékok (1206, ≥ 32 V):** relémodul F100 0,5 A (tekercs-táp); vezérlő F1 **2 A** (D71)
- **Modulmag-táp (D71):** 2 × 10 µF / 16 V (0805) az AP2112K körül
- **Vezérlő-táp apróságai (D59, D61):** 10 Ω-os impulzusbíró ellenállás **2512**-ben (R7), 10 µF / 50 V (1210),
  22 µF / 10 V (1206), 3 × 22 µF / 10 V a 3,3 V-ra
- **Sönt: 1 mΩ, 2512, ≥ 1 W** (LED-modul össz-árama, D47) – 2 db
- Polyfuse-ok: az érzékelők 3,3 V-jára (a modulok V_BUS-án nincs PTC, D55)
- **8 MHz-es kvarc** az STM32-khöz (HSE) – a terhelő kapacitást (CL) a kiválasztott kvarc adatlapjából, ehhez
  igazodik a két kondenzátor
- Ferritgyöngy a VDDA-ra (kis DCR, ≤ 0,1 Ω) vagy 0 Ω
- Passzívok, állapot-LED-ek (piros/zöld) + fényvezetők; ~~NTC~~ → a kézben lévő MCP9701A (D78)
- Iker érvéghüvelyek (két egyszínű szalag egy +24 V-os pólusán)
- DIN-ház: gyári (pl. Camdenboss CNMB) vagy 3D-nyomtatott (D50); a relémodulhoz lángálló anyag
- Stencil a NYÁK mellé (a gyártótól)
- Tartalék, ha a TI elutasít: 3,3 V-os SN65HVD230-as CAN-breakout (a 120 Ω-os ellenállást levenni, D36)

## D78–D79 (2026-10-22) – L433, SN65HVD230, polaritásvédelem
**Kikerül a vásárlásból:**
- 3 × TCAN1044AVDRQ1 a modulokra → a kézben lévő **SN65HVD230D** (86 db); a vezérlőé marad (TI-rendelés)
- B360 (SMC) a vezérlő D1-ére (a D1 kikerült; a D3 B360-a marad)
- NTC 10 k B3435 (LED-modul) → a kézben lévő **MCP9701A**
- STM32F303RET6 – a modulokon **STM32L433RCT3** (75 db kézben); a 8 F303 tartalék

**Új tétel:**
- **NUCLEO-L433RC-P** (ST fejlesztőpanel, ~15 €) – Mouser/DigiKey, a TI-alkatrészekkel együtt
- **BZT52C15** (15 V-os Zener, SOD-123) – 3 db + tartalék (a három GND-ági FET gate-je)
- **25 MHz-es kvarc** a W5500-hoz – Hestore (Balázs döntése: kvarc, nem a kézben lévő oszcillátor)

**Kézből (nem kell venni):** IRFR1205 (vezérlő Q1), IRFR120N (relé Q100), zöld 0603 LED (522 nm, HL-PST-1608U51GC, 150 db).
~~NTMFS5C604NL (LED Q201)~~ – **javítva 10-22: nincs kézben**, meg kell venni (a Q201 FET-je, Mouser/TME).

**LDO (D80):** marad az **AP2112K-3.3** (2 db/modulkészlet: modulmag + bemeneti modul érzékelősín) – kínai kör vagy Hestore;
a TC2117-nek tantál kellene (ESR 0,2–10 Ω). A relé 230 V-os kimenetének sorkapcsa: **5,08 mm-es THT a készletből (D83)** – nem kell venni.

## Beszerzés 2026-10-23 – LCSC a JLC-s NYÁK-rendeléssel, D85 (`hardware/bom/beszerzes.csv`, `hardware/bom/lcsc-kosar.csv`)
Egy készlet (vezérlő + 3 modul) + tartalék. A `gen/beszerzes.py` soronként a legolcsóbb forrást választja (Hestore vagy LCSC,
ÁFA-val; az LCSC-árak a JLC alkatrészkeresőjéből, 1 USD = 360 Ft-tal). Frissítés rendelés előtt: `python3 gen/beszerzes.py --frissit`.

- **LCSC (99 tétel, ~15 200 Ft ÁFA-val, ~33 USD nettó;** + opcionális kábeloldal ~1 250 Ft): minden, ami nincs kézben és nem a
  TI-rendelésből jön. Feltöltés: lcsc.com → BOM Tool → `bom/lcsc-kosar.csv` (LCSC-kód, darab). Szállítás: a JLC-s NYÁK-rendeléssel
  egy csomagban (az LCSC pénztárában ellenőrizni); néhány passzívnál 100 db a minimum (összesen legfeljebb +1–2 eFt).
- **Hestore: nincs rendelés.** A böngészőben összerakott Hestore-kosár (10-22) elavult – üríthető.
- **Később:** Gainta D4MG × 3 + D6MG × 1 (~8 200 Ft, Hestore) – a működő prototípushoz nem kell.
- **Kézben:** ST-Link és Nucleo (programozás, firmware-kezdés), STM32L433, SN65HVD230, MCP9701A, IRFR1205/IRFR120N, relék, zöld LED,
  74HCT14, a relékimenet 5,08-as sorkapcsai (D83).
- **TI-rendelés (8 tétel, ha megjön);** ha nem: ugyanezek az LCSC-n ~6 400 Ft (a `beszerzes.csv` „Alternatíva” oszlopa).
- **Megszűnt / nem kapható → csere (D85):** NTD5C648NL → NCE6080K, NTMFS5C604NL → NCEP6090AGU, Keystone 3568 → NANO² 15 A.
- **Beültetés előtt ellenőrizni:** a kézben lévő 5,08-as sorkapcsok (J101–J104) névleges értéke; a 470 µF-os elkó 20 mm magas (ház);
  a 2 kivezetésű sönt a Kelvin-footprint két-két padját összeforrasztja (szándékos).
