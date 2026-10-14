# CAN a modulbuszon, galvanikus leválasztás, STM32F303RET6 – 2026-10-13

Forrás: Cowork-munkamenet (claude.ai), 2026-09 – 2026-10-13. A szeptemberi rész röviden a végén.
Döntések: D26–D36 a `DONTESEK.md`-ben. Sample-lista: `../SAMPLE-KERESEK.md`.

## CAN az autóiparon kívül (a dolgozat indoklásához)
- Bevett minta: központi egység + saját MCU-s modulok CAN-en.
- **Épületautomatizálás:** a Loxone Link (Miniserver ↔ DIN-sínes bővítők) CAN-alapú, 125 kbit/s, a bővítőket
  sorozatszám alapján címzi – gyakorlatilag ugyanez az architektúra. A Velleman Velbus is CAN-re épül.
- **Más területek:** ipari automatizálás (CANopen, távoli I/O modulok), liftek (CANopen-profil, CiA 417),
  hajózás (NMEA 2000), mezőgazdasági gépek (ISOBUS), hobbi: Klipper 3D-nyomtatók (a fej saját MCU-s panelje
  CAN-en a főpanelen).
- **Érvek 0,5 m-en** (nem a távolság): (1) bármely modul magától üzen, nem kell lekérdezni; (2) hardveres
  arbitráció, CRC, hibaszámlálás; (3) differenciális → elviseli a LED-modul áramától elcsúszó GND-t.
- Ára: modulonként egy transceiver + saját protokoll.
- Az ESPHome `esp32_can` komponense támogatja a C6-ot (2 TWAI vezérlő) – gyors demóhoz jó.

## Vezérlő ≠ transceiver
Az STM32-ben (bxCAN) és a C6-ban (TWAI) csak **CAN-vezérlő** van: keretezés, arbitráció, CRC, nyugta,
hibaszámlálók, szűrés; kimenete két 3,3 V-os logikai láb (CAN_TX, CAN_RX). A **transceiver** a fizikai réteg:
differenciális CANH/CANL meghajtás a 60 Ω-os lezáráson (néhányszor 10 mA – GPIO-val nem megy), domináns/
recesszív állapot, GND-eltolódás- és hibatűrés. Mint Ethernetnél a MAC és a PHY. A transceiver nélküli
„diódás huzalozott ÉS” trükk csak egy NYÁK-on belül, közös földön működik – kábelen láncolt modulokhoz nem.
Az ISO1042 = transceiver + galvanikus leválasztó egy tokban.

## Modul-protokoll (D31, javaslat)
Nem teljes CANopen-stack, hanem annak fogalmai: heartbeat; a regisztertábla olvasása/írása SDO-szerűen;
események PDO-szerűen; a UID-alapú címkiosztás CANopen-megfelelője az LSS. Így a saját protokoll mögött van
egy szabvány, amire a dolgozat hivatkozhat.

## Multi-protocol (D32, javaslat)
- **Node ↔ otthon:** erre a Matter a válasz (ugyanaz az adatmodell Threaden, Wi-Fin, Etherneten).
  C6-korlát: egyszerre egy 802.15.4-stack (Thread VAGY Zigbee), és a Wi-Fi a Threaddel egy rádión osztozik →
  node-onként választható firmware-változat, nem minden egyszerre. MQTT a Wi-Fi/Ethernetes node-okra később
  olcsón hozzáadható.
- **Modulbusz:** egységes marad (nem keverünk CAN-t, I²C-t, RS-485-öt). A protokoll-sokféleség a modulon
  belül van: az STM32 beszélhet I²C-n szenzorral, Modbuson fogyasztásmérővel, DALI-n lámpával, a vezérlő felé
  mindig ugyanaz a CAN-protokoll. Egy RS-485/Modbus átjáró = új modultípus, nem új buszváltozat.

## Audió (D29)
- Kikerül a modulrendszerből: a hangkijátszó egység önálló, saját Wi-Fi-vel. A vezérlőnek nem kell I²S.
- A buszon egyébként sem menne: klasszikus CAN ≤ 1 Mbit/s nyersen, ennek kb. a fele hasznos adat; a
  CD-minőségű sztereó kb. 1,4 Mbit/s. (A C6-ban nincs CAN FD.)

## Modul-MCU: STM32F303RET6 (D27)
- **8 db van.** A korábbi „~20 db STM32, típus ismeretlen” adatot pontosítani kell.
- 1× bxCAN (CAN 2.0B active) → a D19 feltétele teljesül, a CAN marad. Hestore-rendelés most nem kell.
- 512 KB flash, 64 KB SRAM + 16 KB CCM, 72 MHz Cortex-M4F. 25 kHz-es PWM: 72 MHz / 25 kHz = 2880 lépés
  ≈ 11,5 bit (a LED-modulhoz számolt ~11 bit rendben).
- 8 db: 3 a védésre (LED, relé, szenzor) + 5 tartalék.
- **Későbbi olcsóbb MCU:** a G0/G4 családban FDCAN van (más periféria, más HAL), és a G4 LQFP64-es
  lábkiosztása eltér az F303-étól (ST AN5094) → új layout. Ezért a CAN-meghajtó vékony absztrakciós réteg
  mögé kerüljön, hogy a protokollkód hordozható maradjon.
- A CAN-lábakat az adatlap AF-táblázatából kell rögzíteni (ellenőrizendő; a PA11/PA12 az USB-vel közös, de a
  modulon nincs USB).

## Galvanikus leválasztás a modulbuszon (D28)
Balázs célja: bármelyik modul bármikor bármilyen tápra kerülhet, és a tetőtérben / álmennyezetben semmi ne
gyulladhasson ki.

**Mit véd:**
- **Elvesző föld** (a legrosszabb eset): ha a LED-modul vastag GND-je kilazul a sorkapocsban, a 10–20 A-es
  visszatérő áram a JST-lánc GND-erén keres utat (XH ~3 A/tű) → izzó vezeték az álmennyezetben. Izolált
  busszal ilyen út nincs: a LED kialszik.
- Bármely modul bármely tápra / fázisra köthető, a buszon nem folyik kiegyenlítő áram.
- Egy modul hibája (pl. átütött FET) nem terjed át a vezérlőre és a többi modulra.
- Az Ethernet-féle trafós csatolás CAN-nél nem megy (a CAN jelének van egyenáramú összetevője) → izolált CAN
  transceiver. (Ethernet: 1500 V; ISO1042: 5 kV.)
- A specifikáció 3.2.1-es földelési blokkjának „elektromos védőháló” megoldása (ott még I²C-leválasztás)
  így izolált CAN-ként valósul meg.

**Javasolt kiosztás (javaslat):**
- Lánc, JST-XH 4 tű: **V_BUS (5 V), GND_BUS, CAN_H, CAN_L**. **Nincs 24 V a láncon** → a lánckábel zárlata
  nem tud 15 A-es tápot rövidre zárni.
- A V_BUS-t a vezérlő adja, áramkorlátozva (TPS2553 vagy polyfuse) → a busz egyetlen pontból kap referenciát.
- Modulonként izolált CAN transceiver: az egyik oldala a modul saját 3,3 V-ja (saját 24 V → buck), a másik a
  V_BUS. Az izolált transceiverek busz oldala 5 V-ot kér → ezért 5 V a V_BUS.
- **A V_BUS-bemenetet modulonként védeni kell** (polyfuse + 5 V-os TVS): az ISO1042 tápja (VCC2) abszolút
  maximum 6 V – a CAN-lábak bírják a félredugott 24/48 V-ot, a tápláb nem.
- A szenzormodul (nincs nagyáramú terhelés) járhat V_BUS-ról is, akkor nem kell saját táp.
- A tűszám marad, csak a kiosztás változik. A lezárás változatlan (120 Ω a vezérlőn + lezáródugó; osztott
  lezárás).
- Elvetve: ISOW1044 (integrált DC-DC, a láncon nem kellene táp) – drágább, ~47 % hatásfok, a beépített
  konverter miatt EMC-szempontból kényesebb.

**IC-választás → ISO1042BDWVR (D33):**

| IC | Leválasztás | Busz hibatűrés | Beszerzés (2026-10-13) | Megjegyzés |
|---|---|---|---|---|
| **ISO1042BDWVR** (TI) | 5 kVrms | ±70 V | DigiKey: 30 221 db raktáron; nettó 1 702 Ft/1 db, 1 296 Ft/db 10-től; ingyenes szállítás 28 000 Ft felett. LCSC: ISO1042BDWR (16 lábú) 14 db, ~4,67 USD. TME: nincs készleten. | **választott.** CAN FD-képes (a C6 nem használja); a TI új tervekhez ezt ajánlja |
| ISO1050DUBR (TI) | 2,5 kVrms | −27 … +40 V | Hestore: raktáron, nettó 375 Ft/db 5-től; TME: 2694 db | **Elvetve:** 48 V-ot nem bír; nem lábkompatibilis az ISO1042-vel (lásd lent) |
| ISO1540DR (Hestore) | 2,5 kV | – | Hestore: raktáron, 405 Ft/5 db | **Nem jó:** I²C-izolátor (kétirányú, nyitott drain), nem CAN transceiver |

- **ISO1050 ↔ ISO1042 nem csereszabatos:** más tok (ISO1050 DUB: SOP-8, 2,54 mm-es lábtáv; ISO1042 DWV:
  8 lábú SOIC, 1,27 mm-es lábtáv, 7,5 mm széles test) és a 2-es/3-as láb fel van cserélve (ISO1050: 2 RXD,
  3 TXD; ISO1042 DWV: 2 TXD, 3 RXD). A többi láb azonos: 1 VCC1, 4 GND1, 5 GND2, 6 CANL, 7 CANH, 8 VCC2.
- **Footprint:** a DWV 7,5 mm széles testű 8-SOIC – nem a sima (3,9 mm-es) SOIC-8! A DigiKey/TI oldalán lévő
  EDA-modellt érdemes letölteni, vagy a KiCad-footprint szélességét ellenőrizni.

## Beszerzés: csak TI-sample; a NYÁK-on csak az ISO1042 (D35, D36)
- A DigiKey-rendelés (10 db ≈ 16 500 Ft bruttó, 28 000 Ft alatt szállítási díjjal) most nem fér bele →
  **az ISO1042 csak TI-sample-ből jön** (legalább 3 db; ha kevesebb jön, elsőként a LED-modulba). Ha nem
  érkezik meg, a prototípusban nem lesz izoláció – Balázs szerint ez elfogadható.
- **A NYÁK-on csak az ISO1042 (DWV) footprintje van** (D36) – a végleges változatban biztosan az lesz.
  A korábban javasolt kettős footprint (ISO1042 + sima SO-8 transceiver) elvetve.
- **Ha a sample nem jön meg:** izolált transceiver nélkül a modul egyáltalán nem kommunikálna, ezért
  ideiglenesen egy nem izolált 3,3 V-os transceiver-breakout (pl. SN65HVD230) kerül az ISO1042 padjeire:
  1 VCC1 → 3V3, 2 TXD → TX, 3 RXD → RX, 4 GND1 → GND, 5 GND2 a 4-gyel összekötve (drót vagy polyfuse),
  6 CANL, 7 CANH; a 8 VCC2 szabadon marad. A breakoutok többségén van egy 120 Ω-os lezáró ellenállás →
  **le kell venni**, különben a sok párhuzamos lezárás miatt a busz hibázik. A padek körül maradjon hely.
- **Prototípus-szabály nem izolált módban:** minden modul és a vezérlő egy tápról, csillagpontos földdel.
- Ha a TI-kérés elmarad, a vezérlőnek is kell nem izolált transceiver (a TCAN330 is TI-sample) → SN65HVD230 vagy
  MCP2562FD (Microchip-sample). A TME-n az SN65HVD230DR 2026-10-13-án nincs készleten.
- A dolgozatban: az izoláció a terv része, a prototípusban opcionálisan beültetve.

**Mit NEM véd – tűzvédelem a teljesítményúton (D30, javaslat):**
- A biztosíték a vezetéket védi → a forrás (táp) oldalán kell lennie, nem csak a modulon.
- A 15 A-es LED-tápot ágakra bontani (pl. 4 × 4 A, ágonként ≤ 100 W), ágankénti biztosítékkal – a korlátos
  teljesítményű áramforrás logikája (amerikai Class 2 / európai LPS).
- Rugós (push-in) sorkapcsok a modulokon + érvéghüvely mindenhol (a laza csavaros kötés a leggyakoribb
  tűzforrás). Phoenix sample-programból kérhető.
- A 3D-nyomtatott PLA/PETG nem lángálló → az álmennyezetbe/tetőtérbe kerülő modulok V-0 anyagból vagy fém
  dobozban. A relémodul (230 V) rendes elosztódobozba, ne a mennyezetbe.
- Firmware: NTC a FET-ek mellett, túlmelegedésre lekapcsolás – harmadik réteg, soha nem az egyetlen.

## 48 V – esetleges későbbi változat (D34)
- Most **24 V-ra tervezünk.** Később lehet egy 48 V-os változat, pl. a kertbe, ahol nagyobbak a távolságok.
- A busz oldal ehhez kész: az ISO1042 CAN-lábai ±70 V-ot bírnak.
- Akkor kell cserélni a teljesítményoldalt: TVS (az SMBJ28A kb. 45 V-on vág → 48 V-on vezetne), buck (az
  LMR36006 60 V-os → kevés tartalék; 80–100 V-os kell), 60 V-os FET-ek → 100 V-os, 24 V-os relétekercsek,
  kondenzátorok feszültségtűrése.
- Nagyobb távolságnál a CAN kisebb bitrátán bírja (ökölszabály: 125 kbit/s-on ~500 m, mint a Loxone Link),
  de az 5 V-os V_BUS a hosszú kábelen leesne → a busz táplálását akkor újra kell gondolni.
- A bitráta legyen firmware-ből állítható.

## Sample-lista
Külön dokumentumban: `../SAMPLE-KERESEK.md` (TI, onsemi, Würth, Coilcraft, Phoenix, Microchip, ADI;
mennyiségek, tartalékok, mi nem kell már, mit kell megvenni).

## Korábban ebben a munkamenetben (2026-09)
- **Projekt neve: Moduláris okosotthon platform** (Balázs, 2026-09-18: „a modunode-ot felejtsd el”; D26).
  A projektdokumentumokban még ModuNode szerepel.
- **Beadható specifikáció (docx, 2 oldal):** Igény – Ötlet – Megoldás – Specifikáció (összefoglaló táblázat),
  cikkszámok nélkül, a 3.2.1-ben földelési Probléma–Kutatás–Megoldás blokkal. A fájl a Cowork-chatben van,
  a repóban nincs. **Elavult:** még I²C/I²S láncbuszt, MCU nélküli modulokat és audiómodult ír le → frissíteni
  kell (CAN + STM32 + izoláció, audió nélkül).
- **AliExpress prototípus-rendelés (2026-09):** a 11 tételből 9 lett ténylegesen megrendelve; **kimaradt az
  SCT-013-030 áramváltó és az ULN2803A**, az RGBCCT LED-szalag 0,5 m helyett 2 m-es változatban ment. Az
  ULN2803A a relémodulhoz kell → a TI-sample-listán van, különben megvenni.

## Források
- [Loxone Link – mikrocontroller.net](https://www.mikrocontroller.net/articles/Loxone_Link)
- [Velbus – Finder esettanulmány](https://www.findernet.com/en/worldwide/cases/velbus-velleman-group/)
- [CiA 417 – lift-profil](https://www.can-cia.org/can-knowledge/cia-417-series-profile-for-lift-control-systems)
- [ESPHome esp32_can](https://esphome.io/components/canbus/esp32_can/)
- [ST STM32F303RE](https://www.st.com/en/microcontrollers-microprocessors/stm32f303re.html)
- [ST AN5094 – F303 ↔ G4 migráció](https://st.com/resource/en/application_note/an5094-migrating-between-stm32f334303-lines-and-stm32g431xxg474xxg491xx-microcontrollers-stmicroelectronics.pdf)
- [TI ISO1042 adatlap](https://www.ti.com/lit/ds/symlink/iso1042.pdf) · [TI ISO1050 adatlap](https://www.ti.com/lit/ds/symlink/iso1050.pdf) ·
  [TI ISOW1044](https://www.ti.com/product/ISOW1044)
- [DigiKey – ISO1042BDWVR](https://www.digikey.hu/en/products/detail/texas-instruments/ISO1042BDWVR/10434788) ·
  [LCSC – ISO1042BDWR](https://www.lcsc.com/product-detail/C2671499.html) ·
  [TME – ISO1050DUBR](https://www.tme.com/id/en/details/iso1050dubr/can-interfaces-integrated-circuits/texas-instruments/) ·
  [TME – SN65HVD230DR](https://www.tme.com/ca/en/details/sn65hvd230dr/can-interfaces-integrated-circuits/texas-instruments/)
