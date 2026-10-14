# Sample-kérések – 2026-10-13, frissítve 2026-10-14

Az aktuális architektúra (D27–D61) alapján, a 2026-10-10-i lista helyett. Mennyiség: védésre vezérlő +
3 modul (LED 6 csatornás, relé, általános bemeneti modul 16 bemenettel) + tartalék. **Min.** = ami a
prototípushoz kell, **Kérni** = ennyit érdemes kérni (ha a program kevesebbet enged, a minimum a fontos).
A pontos alkatrészek: `MODULMAG-SPEC.md`, `VEZERLO-SPEC.md`.

**2026-10-14:** a modulmag tápja **P78E05-1000 + NCP1117ST33** lett (mindkettő kézben, D56), és a vezérlő V_BUS-át is
a **P78E05** adja (D59) → **az LMR36006 sehol nem kell**; a vezérlő CAN transceivere **TCAN1044AVDRQ1** (D60) a TCAN330
helyett.

Tippek: egyetemi e-mail, a szakdolgozat címe a kérelemben, alkatrészenként 2–5 db, ugyanaz a funkció két
gyártótól. **Most kell kérni:** a döntés (TI) kb. 5 munkanap, a szállítás 1–2 hét; a beültetés a NYÁK
megérkezése után (≈ november közepe) lesz.

## TI – 1. prioritás (hozzáférést kell kérni céges/egyetemi e-maillel)

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
| **TLV75533PDBVR** (TLV755P, 3,3 V, SOT-23-5) | 500 mA-es LDO – a bemeneti modul a V_BUS-ról jár (B változat) | bemeneti modul | 1 | 2 | bármilyen 3,3 V-os LDO SOT-23-5-ben; végszükségben a kézben lévő NCP1117ST33 (SOT-223 – más footprint, ejtés ≤ 1,1 V, a V_BUS-ról még elég) |

Opcionális, ha a limit engedi: **TPS2660** (60 V-os eFuse: túláram + fordított polaritás + túlfeszültség egy
IC-ben, D30). Szóba jöhet a V_BUS-bemenet túlfeszültség-védelmére is – ez **nyitott döntés (D55)**: TVS + PTC
(a mostani terv) vagy eFuse/OVP-kapcsoló modulonként.

## onsemi (MyON fiók, darabszám-korlát lehet)

| Alkatrész | Mire | Hova | Min. | Kérni |
|---|---|---|---|---|
| **NTD5C648NL** (60 V, 4,1 mΩ, DPAK) | LED-csatorna FET – az IPD053N06N helyett, mert az Infineon nem ad sample-t | LED-modul (6 csatorna) | 6 | 8 |
| Schottky, ≥ 5 A, ≥ 60 V (SS56-kategória, SMC) | szabadonfutó dióda drain → +24 V | LED-modul | 6 | 8 |
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
- Relémodul: 4 relé kimenete (≥ 250 V, ≥ 10 A; 8 vagy 12 pólus – COM + NO, ill. + NC) + betáp
- Többi modul és vezérlő: 24 V-os betáp (kis áram)

## Microchip (második forrás, opcionális; a gmail-t elutasíthatja)
- **MCP2562FD** – nem izolált CAN transceiver (5 V + VIO, ±58 V), a TCAN1044AV helyére lábról lábra beültethető – 2 db
- **TC4427** – gate driver tartalék a UCC27524 helyett – 3 db

## Kézben – nem kell kérni (2026-10-14, `beszelgetesek/2026-10-14-alkatreszkeszlet-p78e05.md`)
- **P78E05-1000** (~200 db) – a modulmag 24 V → 5 V-ja (D56) és a vezérlő V_BUS-a (D59)
- **NCP1117ST33T3G** (tekercs) – 5 V → 3,3 V (D56); LM3940 3,3 V (19 db) tartaléknak
- **74HCT14D** (36 db) – a vezérlő RGB LED-jének szintillesztője (U9); **WS2812C-2020** – a vezérlő RGB LED-je lehet
- LM2904 / LM2902, IRFR1205, ACS758LCB-100B, LM2576S – tartaléknak / későbbre

## Már nem kell
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
- Mini lapos (autós) biztosíték NYÁK-foglalattal + 20 A-es biztosíték (LED-modul)
- **SMD-biztosítékok (1206, ≥ 32 V):** modulmag F1 0,5 A (a LED-modulon a 20 A-es biztosíték ELŐTT leágazva, D54);
  vezérlő F1 1 A
- **Modulmag-táp apróságai (D56, D57):** 10 µF / 50 V-os kerámia (1210), 22 µF / 10 V-os kerámia (1206), 10 µF-os
  tantál (3216) az NCP1117 kimenetére, 10 Ω-os impulzusbíró ellenállás (1206, R6, opc.)
- **Vezérlő-táp apróságai (D59, D61):** 10 Ω-os impulzusbíró ellenállás **2512**-ben (R7), 10 µF / 50 V (1210),
  22 µF / 10 V (1206), 3 × 22 µF / 10 V a 3,3 V-ra
- **Sönt: 1 mΩ, 2512, ≥ 1 W** (LED-modul össz-árama, D47) – 2 db
- Polyfuse-ok: **modulonként a V_BUS-ra hold ≈ 0,5 A, ≤ 0,5 Ω** (modulmag F2); az érzékelők 3,3 V-jára
- **8 MHz-es kvarc** az STM32-khöz (HSE) – a terhelő kapacitást (CL) a kiválasztott kvarc adatlapjából, ehhez
  igazodik a két kondenzátor
- Ferritgyöngy a VDDA-ra (kis DCR, ≤ 0,1 Ω) vagy 0 Ω
- Passzívok, állapot-LED-ek (piros/zöld) + fényvezetők, NTC (a FET-ek mellé, D30)
- Iker érvéghüvelyek (két egyszínű szalag egy +24 V-os pólusán)
- DIN-ház: gyári (pl. Camdenboss CNMB) vagy 3D-nyomtatott (D50); a relémodulhoz lángálló anyag
- Stencil a NYÁK mellé (a gyártótól)
- Tartalék, ha a TI elutasít: 3,3 V-os SN65HVD230-as CAN-breakout (a 120 Ω-os ellenállást levenni, D36)
