# Végleges LED-modul, node/modul architektúra, modul-busz – 2026-10-10/11

Forrás: claude.ai „szakdolgozat” Projekt, a LED-vezérlő modulról indított chat (2026-10-10 este – 10-11).

## Fogalmak (Balázs)
- **Node** = egy ESP32-C6 vezérlő + a hozzá csatlakozó modulok. A node-ok Matter over Thread, WiFi vagy Ethernet
  kapcsolattal mennek a HA-hoz. Lesz node szekrényben, polcon, íróasztalon, konyhában stb.
- **Modul** = egy feladatot ellátó, csatlakoztatható eszköz (LED, relé, szenzor), saját MCU-val (STM32; kb. 20 db
  van kézben, a pontos típus még nincs meg).
- Vezérlő–modul távolság legfeljebb 0,5 m; a modulok egymás után, JST-szerű csatlakozóval (lánc).
- Védésre legalább 2, inkább 3 modul. A NYÁK-ot legkésőbb 3 héten belül (≈ 2026-10-31) meg kell rendelni.

## Végleges LED-modul
- Követelmény: szalagonként (modulonként) a FET-ek bírjanak 10 A-t, a PWM legyen 20 kHz felett, a vezérlés a buszon.
- **Driver, nem közvetlenül hajtott logic-level FET.** 3,3 V-on a logic-level FET sem nyit ki biztosan
  (pl. AOD4184A: az Rds(on) csak 4,5 V-ig adott, Vth max. 2,6 V), egy PWM IC kimenete pedig kevés áramot ad
  (PCA9634: 10 mA) → kb. 1 µs-os átkapcsolás, 25 kHz-en, 10 A-en 3–4 W csatornánként. Driverrel 20–40 ns,
  kb. 0,1 W kapcsolási + 0,8–0,9 W vezetési veszteség, hűtőborda nélkül.
- Javasolt fokozat:
  - **UCC27524** (TI): kétcsatornás, 5 A, 4,5–18 V, kb. 2 V-os bemeneti küszöb (3,3 V-os logikával megy),
    bemeneti lehúzás (lebegő bemenet = KI), UVLO alatt a kimenet alacsony. 12 V-ról (78L12) táplálva.
  - **60 V-os normál FET**, pl. Infineon IPD053N06N: 5,3 mΩ @ 10 V, 27 nC, DPAK. 12 V-os meghajtásnál nem kell
    logic-level; a magasabb küszöb jobban bírja a zajt. 60 V a hosszú szalagvezeték tüskéi miatt.
  - Csatornánként: 10 Ω gate-ellenállás (EMC miatt 22–47 Ω), 10 kΩ G–S, Schottky (pl. SS56) drain → +24 V;
    a 24 V-on 470 µF + 100 nF.
- Csatornánként 10 A; a maximális fényerős CCT-keverés miatt a közös +24 V / GND út 20 A-re.
- PWM-forrás: a modul STM32-je (25 kHz-en kb. 11 bit). Elvetve: PCA9685 (≤ 1,5 kHz), PCA9634/35 (97 kHz, de csak
  8 bit → kis fényerőn lépcsős, CCT-nél ugráló szín).

## Modul-busz
- 0,5 m-en a távolság nem érv. A CAN mellett szól:
  - automatikus címkiosztás az STM32 96 bites UID-jával, plusz vezeték nélkül;
  - a modul magától jelez (pl. ajtó), nem kell lekérdezni;
  - differenciális → bírja a LED-modul áramától eltolódó GND-t;
  - ESP32-C6: 2 TWAI vezérlő (CAN FD nincs), modulonként egy 3,3 V-os transceiver (pl. TI TCAN330).
- Az RS-485 itt nem ad többet a CAN-nál; az I²C + PCA9615 3 m-ig jó, de csak a mester kezdeményezhet.
- Csatlakozó: JST-XH, 4 tű: +24 V, GND, CAN_H, CAN_L. Lezárás: 120 Ω a vezérlőn + lezáródugó (JST-dugó benne
  120 Ω-mal) a lánc végén.
- **Feltétel: az STM32-ben legyen CAN** (pl. F103, F072, G0B1, G4). Ha nincs: I²C + közös INT vonal + láncvezeték
  a címkiosztáshoz (6 tű).

## Okos modulok, bootloader
- Egységes regisztertábla: típus, HW/FW verzió, UID, képességek, állapot, hőmérséklet, hibaszámlálók.
  Ebből a vezérlő tudja, mit hozzon létre a Matterben.
- Bootloader (8–16 KB a flash elején):
  - az alkalmazás eltolt címre linkelve, vektortábla áthelyezve;
  - ha az alkalmazás CRC-je hibás vagy a vezérlő frissítést kér, a bootloaderben marad;
  - CAN-protokoll: kezdés (méret, CRC, verzió) → 8 bájtos darabok sorszámmal és nyugtával → ellenőrzés → újraindítás;
  - a modul-firmware-ek a C6 flash-én, a vezérlő verzió alapján frissít (node OTA → a modulok is frissülnek);
  - a bootloader nem írja felül önmagát → áramszünet frissítés közben nem téglásít.
- Kész alternatíva: OpenBLT (STM32, CAN, GPLv3). Egyes STM32-k ROM-bootloadere is tud CAN-t.
- A NYÁK-hoz kell: SWD minden modulon, BOOT0 pad, ≥ 64 KB flash. A bootloader ráér a rendelés után.

## Matter: a node Matter-híd
- Aggregator endpoint + modulonként Bridged Node endpoint. Új modul futás közben, újrapárosítás nélkül jelenik meg a
  HA-ban (esp-matter `blemesh_bridge` példa: csatlakozáskor dinamikus endpoint).
- Bridged Device Basic Information: név, UniqueID = STM32 UID, **Reachable** (kihúzott modul → „nem elérhető”, az
  eszköz és az automatizálások megmaradnak).
- UID → endpoint hozzárendelés a node NVS-ében; endpoint-ID-t nem használ újra (`min_uu_ep_id`).
- Buktató: a HA matter.js-alapú Matter-szerverében 2026-ban hiba volt a futás közben hozzáadott endpointokkal
  (a HA Matter-integrációja újratöltődött; matterjs-server #1016, javítás: PR #1077). Tesztelni kell; ha gond van,
  az eszköz újrainterjúja elég.
- A bridge-re váltás egyszer újrapárosítással jár (az 1. endpoint típusa változik).

## Állapotkezelés
- Busz megszakad vagy a vezérlő újraindul → a modul tartja a kimeneteit, a HA-ban Reachable = false.
- A modul kap áramszünetet → a hiteles állapot a vezérlőnél van, visszaküldi, amint a modul újra jelentkezik
  (a modul nem ment állapotot a flash-be).
- Az egész node áramtalanodik → a Matter StartUpOnOff dönt (a CCT szalagnál KI).

## Tápelosztás – buktatók
- A JST-láncon csak logikai táp megy (XH kb. 3 A/tű, PH kb. 2 A/tű); a LED-modulnak saját sorkapocs + biztosíték.
- Földhurok: egy csillagpont a táp „–” pólusán; a nagyáramú hurok a modulon belül záródjon.
- 24 V bemenet: TVS (pl. SMBJ28A, kb. 45 V-on vág) → a buck legalább 60 V-os (pl. TI LMR36006; a 36 V-os LMR51420
  kevés). Fordított polaritás ellen P-FET (SUM110P08 van).
- Bedugás üzem közben: a kondenzátorok áramlökése resetelheti a vezérlőt, a JST nem üzem közbeni dugásra készült →
  lágyindítás (lassan nyitó P-FET) vagy csak feszültségmentesen bővíteni.
- Logikai táp modulonként buckkal (LDO-val 24 → 3,3 V már 20–30 mA-nél 0,4–0,6 W).

## EMC olcsón
- Ingyen: fázistolás a csatornák között, frekvencia-dithering (±5–10 %), lassabb él (22–47 Ω gate,
  kb. 0,3–0,5 W/csatorna), pufferkondenzátor a FET-ek mellett, sodrott szalagvezeték.
- Fillérekért: Schottky a drainen, TVS a bemeneten; CAN ESD-dióda (Nexperia PESD2CAN vagy TI ESD2CAN24) és osztott
  lezárás (2 × 60 Ω + 4,7 nF).
- Csak footprint (0 Ω-mal áthidalva vagy beültetés nélkül): RC-snubber a FET-eken, CAN közös módusú fojtó, ferrit a
  24 V bemeneten. Alkatrész csak mérés alapján kerül bele.

## Sample-ek (2026-10-10-i állapot)
| Cég | Feltételek | Mit kérnénk |
|---|---|---|
| Analog Devices | ingyenes; 2 db/alkatrész, max. 4 féle / 14 nap; céges vagy egyetemi e-mail | ADE7953, ADM2587E (izolált RS-485), LTC2862 |
| TI | hozzáférést kell kérni a sample programhoz céges e-maillel, 5 munkanapon belül döntenek | UCC27524, TCAN330, THVD1450, LMR36006, TPS2660, INA181 |
| onsemi | 1000+ féle ingyenes, MyON fiók, darabszám-korlát lehet | 60 V FET-ek, Schottky, LDO |
| Würth Elektronik | ingyenes alkatrész szakdolgozathoz/projektmunkához, kapcsolatfelvételi űrlapon | passzívok, sorkapcsok, RJ45, ferrit, TVS |
| Coilcraft | ingyenes, diákok „észszerű mennyiséget” kérhetnek | tekercsek, közös módusú fojtó |
| Phoenix Contact | ingyenes, ingyenes szállítással, 3000+ tétel | sorkapcsok, NYÁK-csatlakozók |
| Microchip | microchip.com/samples; beszámolók szerint gmail-t elutasíthat, rendeléskorlát | TC4427, MCP2562FD |
| ST / NXP / Infineon | nincs nyilvános egyéni sample-rendelés (ST: egyetemen vagy helyi irodán át) | – |
| PCBWay | diák-szponzoráció; a szállítás fizetős, projektleírás kell | NYÁK |

Tippek: egyetemi e-mail, a szakdolgozat címe a kérelemben, alkatrészenként 2–5 db, ugyanaz a funkció két gyártótól.
Most kell kérni: a szállítás 1–2 hét, különben TME/Mouser.

## NYÁK-terv (3 hét)
- 4 panel: vezérlő, LED-modul (CCT, 2 × 10 A), relémodul (4 Schrack), szenzormodul (AH1911 + pl. hőmérséklet/pára).
- Közös „modulmag”: STM32 + CAN transceiver + 60 V-os buck + 2 JST (be/ki) + SWD + állapot LED + lezáró jumper.
  Egyszer tervezve, mindhárom modulba bemásolva.
- Reflow-kemence van → QFN, TSSOP, PowerPAD is mehet.
- 1. hét: döntések + kapcsolási rajzok; 2. hét: layout; 3. hét: átnézés + rendelés.
- Blokkol: az STM32-k pontos típusa (van-e CAN, mekkora a flash).
