# NYÁK-rajzolás előtt eldöntendő – 2026-10-13, frissítve 2026-10-14

> **2026-10-20/21 – D71–D73 felülírja:** a modulokon nincs P78E05/NCP1117/ISO1042/GND_BUS (központi 5 V, közös föld,
> TCAN1044AV, AP2112K); a vezérlőn LMR33630 + LM66200 + TPS2595; 12–26 V; a ház Gainta D4MG, NYÁK 86,5 × 68 mm
> (bemeneti 86,5 × 103 mm). Az alábbi régi pontok ennek fényében olvasandók; a friss állapot a két specben van.
>
> **2026-10-22 – D78–D80:** modul-MCU **STM32L433RCT3** (a LED-modulon a CH4–CH6 TIM15/TIM16 a PB14/PB15/PB8-on, az I_SENSE a
> PA3-on, a VIN_SENSE a PB1-en; a COMP2 a TIM1/TIM15/TIM16 break-jét állítja le), modul-transceiver **SN65HVD230**,
> polaritásvédelem **N-FET a GND-ágban** (vezérlő Q1, LED Q201, relé Q100 – az LM74700 és a vezérlő D1-e kikerült),
> hőmérő **MCP9701A** (az NTC helyett), LDO **AP2112K** marad, **1 oz + fedetlen nagyáramú sávok (D82, a D79 2 oz-a helyett)**, csavaros sorkapocs a LED-modul
> 20 A-es útján. A lent áthúzás nélkül maradt régi részletek (TIM8, PA7, F303, 4,7 kΩ, NTC) ennek fényében olvasandók.

Ütemterv (D25): kapcsolási rajzok 10-13 – 10-19, layout 10-20 – 10-26, átnézés + rendelés 10-27 – 10-31.
Ami az A részben van, az nélkül nem lehet elkezdeni a rajzot; a B rész a kapcsolási rajz közben, a C rész a
layout előtt kell. A v2-re halasztott dolgok: `V2-OTLETEK.md`.

**A részletes kapcsolási specifikációk (minden alkatrész értékkel, minden bekötés, lábkiosztás) – a KiCad-rajz
innen indul:**
- `MODULMAG-SPEC.md` – a modulmag, lábkiosztás mindhárom modulra
- `VEZERLO-SPEC.md` – a vezérlő (ESP32-C6, táp + USB, W5500, CAN, USB-C)

## A – Blokkolók
- [x] **Modulmag specifikálva** (2026-10-13, `MODULMAG-SPEC.md`, javaslat): **P78E05-1000 + NCP1117ST33**
      (24 V → 5 V → 3,3 V; 2026-10-14 óta, D56 – az LMR36006BRNXR helyett), STM32F303RET6 + 8 MHz, ISO1042BDWVR,
      2 × XH, sima 120 Ω-os lezárás jumperrel, V_BUS-on TVS (PTC nincs, D55), HW-azonosító, 1 × 7-es debug-tüskesor
      (SWD + UART). Mindhárom modul saját 24 V-ról jár; opcionális buszos táp (D66).
- [x] **Vezérlő specifikálva** (2026-10-14, `VEZERLO-SPEC.md`, D58–D61): ESP32-C6-WROOM-1-N16, 3,3 V: LMR36015,
      5 V / V_BUS: P78E05 + TPS2553 (382/425/476 mA), TCAN1044AV (±58 V, jumperes tartalékkal), W5500 + MagJack,
      USB-C (táp busz nélkül), 2 átmenő XH, RGB LED + táp-LED, debug-tüske.
- [x] **LED-modul: 6 csatorna** (D43) → 2 × RGB, 3 × CCT vagy 6 × egyszínű. 3 × UCC27524, 6 FET + 6 Schottky.
  - Low-side kapcsolás → a szalagok közös vezetéke a **+24 V**, nem a GND.
  - Kimenet: 3 × 3 pólusú push-in blokk – [+24 V, CH1, CH2] [+24 V, CH3, CH4] [+24 V, CH5, CH6]. CCT:
    blokkonként egy szalag; RGB: három egymást követő csatorna, bármelyik +24 V-ról; egyszínű: két szalag egy
    +24 V-on, iker érvéghüvellyel.
  - Csatornánként 10 A, össz-áram max. 20 A (firmware-korlát a csatornák összegére).
  - Betáp: 2 pólusú push-in 2,5 mm²-hez, 3 eres kábel – barna +24 V, kék GND, a zöld-sárga nem használható
    (védőföld színe); a kábelt „24 V DC” jelöléssel, hogy ne kössék 230 V-ra. 15 A-es NANO² (D85; korábban 20 A-es mini lapos) biztosíték
    NYÁK-foglalatban. **A modulmag 24 V-ja a főbiztosíték ELŐTT ágazik le** (saját 0,5 A-es F1-gyel) → a kiégett
    főbiztosíték jelezhető (D54).
  - PWM: TIM1 CH1–3 (PA8–PA10) = CH1–CH3 + TIM8 CH1–3 (PC6–PC8) = CH4–CH6, szinkronizálva, 25 kHz (D54).
  - **Mérés (D47, D53):** bemeneti 24 V (VIN_SENSE, PC1) és a biztosíték utáni sín (V_RAIL_SENSE, PC2); össz-áram
    1 mΩ-os söntön (2512, ≥ 1 W, Kelvin) a közös visszatérő ágban + **INA181A2 (×50)** → PA7 (ADC2 + COMP2 nem
    invertáló bemenete; csak gyors anti-aliasing RC). A COMP2 küszöbe a DAC1-ről (alapból ~22 A), a kimenete a
    TIM1 és a TIM8 BKIN2-jére → hardveres túláram-lekapcsolás. A logikai föld a sönt GND-sorkapocs felőli
    oldalán csatlakozzon. Csatornánkénti áram nincs – induláskori önteszt + kitöltés-alapú becslés.
  - DRV_EN (PB12): a három UCC27524 EN-lába közösen, 4,7 kΩ lehúzással (boot alatt tiltva). NTC: PC3.
- [x] **Relémodul:** fogyasztásmérés nincs a v1-ben → v2 (D37). Javaslat: nem foglalunk neki helyet (nincs
      megerősítve). Relé-GPIO-k: PB12–PB15 → ULN2803A (D54).
- [x] **Általános bemeneti modul: 16 bemenet** (D44, D48), mindegyik külön 3 tűs csatlakozón; **bővítő tüskesor
      nincs** – több bemenethez még egy modul kerül a láncra.
  - Csatlakozó: **3 tűs JST-PH javasolt** (D51) – keskenyebb, és nem dugható a busz XH-jába.
  - Lábak (D54): IN0–IN3 PA0–PA3, IN4–IN6 PA4–PA6, IN7 PA7, IN8–IN10 PA8–PA10, IN11 PB11, IN12–IN15 PB12–PB15 –
    mind külön EXTI-vonalon; 12 ADC-képes (IN8–IN10 csak digitális). HDC3020: I²C1, PB8/PB9.
  - **D66:** a modul is saját 24 V-ról jár (A változat, izolált); 24 V nélkül a modulmag D6 + JP2-je (buszos táp).
    Érzékelő-táp: 4 csoport × 4 csatlakozó, csoportonként 3,3 / 5 V-os forrasztható választó + PTC, külön NCP1117.
  - Bemenetenként: soros ellenállás + ESD (4 × TPD4E05U06) + opcionális felhúzó/lehúzó-ellenállás footprint
    (osztóként 12/24 V-os jelhez is). Az ESD a soros ellenállás után, az MCU-oldalon (így magasabb bemenő
    feszültségnél az ellenállás korlátozza az áramot).
  - Az érzékelők 3,3 V-ja polyfuse-on át (egy zárlatos érzékelő ne vigye le a modult).
  - A fel nem használt STM32-lábak firmware-ben analóg módban.
- [x] **Vezérlő: Ethernet közvetlenül a NYÁK-on** (D45): W5500 + MagJack + 25 MHz-es kvarc, a WIZnet
      referencia-kapcsolása szerint, opcionálisan beültetve; PoE nélkül (v2).
- [x] **Vezérlő tápja** (D46 → D59): LMR36015 → 3,3 V; a V_BUS-t (és a CAN transceivert) a kézben lévő P78E05 adja
      (5,0 V ± 3 % → a modulon legrosszabb esetben ~4,7 V, az ISO1042-nek 4,5 V kell – szűken belefér).
- [x] **V_BUS-védelem a modulokon (D55, 2026-10-14):** nincs 24 V elleni védelem (a láncon nincs 24 V), a PTC
      kikerült, az 5 V-os TVS marad (ESD); a V_BUS-mérleg pontosítva (D64).
- [x] **Schrack relé (D62, 2026-10-14):** RTD14024 (16 A, 5 mm-es lábtáv) – KiCad-footprint:
      `Relay_THT:Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm`; kimenet COM + NO (4 × 2 pólus); 230 V-ra tervezve.
- [x] **Buszcsatlakozó: JST-XH** (D38). Tűsorrend minden lapon: 1 V_BUS, 2 GND (D71: közös föld), 3 CAN_L, 4 CAN_H (a CAN-érpár
      egymás mellett, sodorva). Laponként 2 db, egyenesen átkötve – a vezérlőn is (D58).
- [x] **Lezárás: jumper** minden modulon és a vezérlőn (D49, D52) – **sima 120 Ω** a CAN_H és a CAN_L között, a
      jumperrel sorban; csak a lánc két végén bedugva. A jumper a felső vállon, a buszcsatlakozók mellett.
- [ ] **Mechanika** (D50, javaslat) – lásd lent.

## Mechanika (D50, javaslat)
**Ház-forma: DIN 43880** (mint a kismegszakítók): 90 mm magas, a fedél kivágásán kiálló előlap 45 mm,
szélesség 17,5/18 mm-es modulosztásban (pl. 4 M ≈ 70–71 mm, 6 M ≈ 105–106 mm), kb. 53–58 mm mély.
A NYÁK a ház alján fekszik (párhuzamos a sínnel). Előny: elosztószekrény fedele alá is befér, a kábelek a
vállakon a kábelcsatornába futnak, és van hozzá kereskedelmi ház is.

**Csatlakozók helye (minden lapon ugyanígy):**
- **Felső váll:** 24 V-os betáp + CAN-busz BE és KI (2 × XH) + lezáró jumper. A szomszédos modulok között rövid
  buszkábel.
- **Alsó váll:** a „terepi” csatlakozók – LED-kimenetek, relékimenetek (230 V), érzékelők.
- **Előlap (45 mm-es sáv):** állapot-LED-ek fényvezetővel (a NYÁK kb. 40 mm-rel lejjebb van); a vezérlőn a
  RESET/BOOT gomb is (tűvel elérhetően).
- A relémodulon így a 230 V (alul) és a törpefeszültség (felül) természetesen szétválik → a kúszóút könnyebb.

**Becsült méretek:**

| Lap | Ház | NYÁK kb. | Felső váll | Alsó váll |
|---|---|---|---|---|
| Vezérlő | 4 M (~71 mm) | **86,5 × 68 mm** (D73) | 24 V be, busz BE/KI (2 × XH), jumper, USB-C | RJ45 |
| LED-modul | 4 M | **86,5 × 68 mm** (D73) | 24 V be (2,5 mm², 20 A), busz BE/KI, jumper | 3 × 3 pólusú kimenet (~45–50 mm) |
| Relémodul | 4 M | **86,5 × 68 mm** (D73) | 24 V be, busz BE/KI, jumper | 4 relé kimenete (4 × 2 pólus, COM + NO) |
| Bemeneti modul | 6 M (~106 mm) | **86,5 × 103 mm** (D73) | 24 V be, busz BE/KI, jumper + ~6 bemenet | ~10 bemenet |

- Egy 3 tűs XH kb. 10 mm, egy PH kb. 8 mm széles → 16 XH a busz mellett a 6 M-es ház vállain már nagyon szoros,
  PH-val kényelmes (D51).
- **A NYÁK-ot egy kereskedelmi DIN-ház belső méretére tervezni** (pl. Camdenboss CNMB, 6 M: 106 × 58 × 90 mm), és
  a 3D-nyomtatott ház ugyanezt a formát követi → mindkettő jó. A ház adatlapjából: NYÁK-méret, rögzítőfuratok,
  a vállak alatti magasság (a csatlakozók magassága ehhez – **és az elkók, relék magassága**, D73).
- A LED-modul 3 M-be (~53 mm) is beférne, de 6 FET kb. 6 W-ja zárt dobozban → a 4 M több rézfelületet ad hűtésre.
- **Vezérlő-antenna:** az ESP32-C6 modul antennája az előlap felőli, felső sarokban, alatta réz nélkül. **Fém
  elosztószekrényben a rádió nem működik jól** → ESP32-C6-WROOM-1U (U.FL, külső antenna) – a padjai (az EPAD is) az Espressif
  adatlapja és KiCad-footprintjei szerint pontosan ugyanott vannak, telepítéskor választható (D63).
- 3D-nyomtatás: a relémodul háza lángálló anyagból (pl. PC-FR / ASA-FR) vagy gyári ház (D30); DIN-klipsz
  nyomtatva (PETG) vagy vásárolt.

## 4 rétegű NYÁK (D42)
- Ár: a tényleges méretekkel a JLC-ajánlatkérőben ellenőrizni (2026 augusztusában árkorrekció volt). A 4 réteges
  lap gyártási ideje 2–5 nap (a 2 rétegesé ~24 óra) – a határidőbe belefér.
- Rétegrend: jel / GND / táp / jel. A belső rétegek réze a JLC-nél alapból 0,5 oz → **a nagyáramú utak a külső
  rétegeken** (1 vagy 2 oz), belül csak sík és jel. **D82: minden lap 1 oz** (a JLC alapbeállítása; a 2 oz-hoz ≥ 0,2 mm szélesség/távolság
  kellene, az LQFP-64 padjai közti rés épp ennyi). A nagyáramú sávok **fedetlenek**, beültetés után ónnal vagy vezetékkel
  megerősítve – lásd lent: „A 20 A-es út”.
- ~~Az ISO1042 alatti izolációs rés~~ – D71 óta nincs izoláció; helyette: a LED-modul 20 A-es visszatérő útja ne a
  busz-csatlakozók alatt menjen (csillagpont, közös föld).
- **Ethernet:** a két differenciális érpár 100 Ω-os, az USB D+/D− 90 Ω-os – a sávszélességet/rést a JLC
  impedancia-kalkulátorával, a választott rétegrendre számolni; rövid, folytonos GND-sík fölött, via nélkül.
- **C6-antenna:** a panel szélén, alatta egyik rétegen se legyen réz; az RJ45 és a fém alkatrészek távol tőle.
- Kisebb lap ugyanabból: SMD alkatrészek csak a felső oldalon (otthoni reflow, egy menet), debug 2,54 mm-es
  tüskesoron, passzívok 0603-ban. **Stencilt is rendelni** a NYÁK mellé (a vezérlő VQFN-HR buckja és a W5500
  miatt). Furatszerelt: a relék, a sorkapcsok, az XH/PH és a nagy elkók – a reflow után kézzel.

## B – A kapcsolási rajz közben rögzítendő
- [ ] **STM32 lábkiosztás ellenőrzése STM32CubeMX-ben – L433 (D78, D79; `hardware/cubemx/`):** CAN PA11/PA12,
      USART3 PC4/PC5, SWD, HSE, HW-ID PC0, VBUS_SENSE PC1, HW_REV PB0, VIN_SENSE PB1; LED-modulon TIM1 (PA8–PA10) +
      TIM15 (PB14/PB15) + TIM16 (PB8), PA3 → ADC1_IN8 + COMP2, DAC1 → COMP2 INM, COMP2 → TIM1/TIM15/TIM16 break;
      relé PB12–PB15; bemeneti modul 16 bemenet + I²C1 PB8/PB9. A `gen/ellenorzes.py` a lábakat az L433-adatbázisból
      már ellenőrzi (10-22) – a CubeMX-ben a belső kapcsolatokat kell megnézni.
- [x] **Kvarc az STM32-re (HSE, 8 MHz)** – a CAN pontos órajelet kér. Rajz közben: a választott kvarc CL értékéből a
      két terhelőkondenzátor (`MODULMAG-SPEC.md` 3.2); a W5500 25 MHz-ese ugyanígy (`VEZERLO-SPEC.md` 4.3).
- [x] **Teljesítménymérleg:** modulonként < 100 mA a 3,3 V-on (P78E05 1 A, az NCP1117-en ~0,17 W); vezérlő: 3,3 V
      ≈ 0,54 A (LMR36015, 1,5 A), 5 V ≤ 0,61 A (P78E05, 1 A), 24 V-on ≈ 0,25 A (`VEZERLO-SPEC.md` 11.); V_BUS worst
      case ≈ 0,3 A < TPS2553 min. 382 mA; 12 V a gate drivereknek (MC78L12).
- [ ] **A 20 A-es út (LED-modul) – D82: 1 oz, fedetlen sáv, utólag megerősítve.** Huzalozás:
      - a sávot a felső **és** az alsó rétegen is kiönteni, sűrű vián-sorral összekötve (0,6/0,3 mm-es via ~1 A-t bír, 20 A-hez
        ≥ 20 via, a sáv mentén elosztva); 1 oz-on 10 A ≈ 4,5 mm, 20 A ≈ 12 mm (IPC-2221, 10 °C) – ónozva ennek töredéke is elég;
      - **a lakk kihagyása KiCad-ben:** a sáv fölé ugyanakkora kitöltött alakzatot rajzolni az **F.Mask** (alul a **B.Mask**)
        rétegre – a maszkrétegen rajzolt alakzat nyílást jelent; a nyílás ~0,1 mm-rel kisebb legyen a réznél;
      - melyik sáv: +24 V (J201 → F201 → sín → F202–F204 → J202–J204), a drain-sávok a sorkapcsokig, a visszatérő út
        (FET-source-ok → PGND_SH → sönt → GND → Q201 → J201); relémodul: COM/NO a relétől a J101–J104-ig;
      - **a sönt (R209) környékét nem szabad ónozni**: a Kelvin-pontok közti réz része a mérésnek – a nyílás a sönt padjai előtt
        érjen véget; beültetés után: ónozás vagy 1–1,5 mm²-es csupasz rézhuzal a sáv mentén;
      eredeti szöveg: sávszélesség ~6 mm (IPC-2221, 10 °C),
      sorkapocs- és biztosítékértékek, a sönt helye. A nagyáramú út legyen rövid: sorkapocs → FET → sönt → sorkapocs.
- [x] ~~**Védelem helye:**~~ → D71 (a modulmag a buszról jár) és D78 (N-FET a GND-ágban). Régi szöveg: a modulmag logikai tápján Schottky (SS16) a fordított polaritás ellen + SMBJ28A +
      **kötelező 47 µF-os elkó** + opcionális 10 Ω soros ellenállás (spec 2. fejezet, D57; a P78E05 bemenete max.
      36 V, a 24 V-os tápot ≤ 26 V-ra állítani); a 20 A-es úton is legyen-e (nagy P-FET, pl. a kézben lévő
      SUM110P08) – nyitott.
- [ ] **230 V-os oldal (relémodul):** nagy kúszóút és légköz a törpefeszültségű résztől, hasíték a relék alatt;
      a pontos értéket a relé adatlapjából / a szabványból venni.
- [ ] **Olcsó, de utólag már nem pótolható extrák:** tesztpontok (CAN_TX/RX, V_BUS, 3V3, 5V, 24 V, GND, INA-kimenet,
      DAC1 a PA4-en; a vezérlőn GPIO4/5/22/23), UART debug, **HW-típus-azonosító** (osztó a PC0-n – LED / relé /
      bemeneti modul más-más sávban, spec 3.5), 24 V-os bemeneti feszültségmérés minden modulon és a vezérlőn, hőmérő (MCP9701A, D78) a
      FET-ek között (D30), állapot-LED, EMC-footprintek (D24).
- [x] **Vezérlőpanel** (`VEZERLO-SPEC.md`): C6-lábak (3.2), W5500 SPI + INT + RST, USB-C (GPIO12/13, 22 Ω), BOOT/RESET
      gomb, TCAN1044AV + sima 120 Ω-os lezárás jumperrel, V_BUS: P78E05 + TPS2553 (EN a 24 V-os ágról).
- [ ] **Minden alkatrésznél legyen B-terv ugyanarra a footprintre** (a sample-ök bizonytalansága miatt) – ahol
      nincs (pl. a vezérlő LMR36015-je, W5500), azt meg kell venni.

## C – Layout előtt
- [x] **A DIN-ház kiválasztása** → Gainta D4MG / CamdenBoss CNMB/4 / OKW RAILTEC C, NYÁK 86,5 × 68 mm (D73, 2026-10-21).
- [ ] **Footprint-ellenőrzés** a nem szokványos tokoknál: ISO1042 DWV (7,5 mm széles test), LMR36015 (VQFN-HR,
      RNX – csak a vezérlőn), **P78E05 (SIP-3)**, TPD4E05U06 (USON), W5500 + MagJack, USB-C aljzat, Schrack relé,
      sorkapcsok (DG128, KF128), NANO²-biztosítékok, 2512-es sönt, JST-XH és -PH. Nyomtasd ki 1:1-ben, és tedd
      rá a kézben lévő alkatrészt.
- [ ] **Gyártói tervezési szabályok** (JLC / PCBWay, 4 réteg) és a rétegrend betöltése a KiCadbe.
- [ ] **4 külön terv vagy egy panel** (költség).
- [ ] **KiCad-struktúra:** a modulmag hierarchikus lap, amit minden modul ugyanabból a fájlból használ → egyszer kell
      megtervezni és javítani. A modulmag layoutja is újrahasználható blokk (`MODULMAG-SPEC.md` 8. fejezet).
