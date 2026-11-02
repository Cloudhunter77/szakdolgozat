# Moduláris okosotthon platform – komponenslista a kapcsolási rajzokhoz

Ez a lista a kapcsolási rajzok minden alkatrészét felsorolja: mit csinál, és miért van ott. Laponként (vezérlő, modulmag, LED-, relé- és bemeneti modul), azon belül funkcionális blokkonként van rendezve, így a rajz mellett nézegetve egy-egy alkatrész szerepe gyorsan visszakereshető. Az azonos szerepű alkatrészek (pl. a hat LED-csatorna elemei) együtt szerepelnek.

A rendszer felépítése röviden: egy vezérlő (ESP32-C6, Matter-híd a Home Assistant felé) és modulok (LED, relé, bemeneti), amelyek egy 4 eres JST-XH buszon láncban csatlakoznak: 1 = +5 V (V_BUS), 2 = GND, 3 = CAN_L, 4 = CAN_H. A busz 5 V-ját a vezérlő állítja elő, minden modul logikája erről jár. A nagy fogyasztók (LED-szalag, relétekercsek) a saját 12–26 V-os betápjukat kapják, a föld közös. Minden modulon saját mikrovezérlő (STM32L433) van, a modulok CAN-en kommunikálnak a vezérlővel.

A modulmag egy közös hierarchikus lap: a LED-, a relé- és a bemeneti modulon ugyanaz (mikrovezérlő, táp a buszról, CAN, busz-csatlakozók). Ezért külön fejezetben szerepel, a moduloknál csak a modulspecifikus rész van.

Jelölések: DNP = az alkatrész helye (footprintje) a NYÁK-on van, de alapból nincs beültetve (későbbi bővítés vagy mérés utáni hangolás).

Állapot: 2026-11-01 (STM32L433 a modulokon, izolált CAN-transceiver a modulokon – a LED-modul leválasztva a busztól, polaritásvédő FET a GND-ágban, AP2112K-s 3,3 V; a konzulensi átnézés után: NRST-felhúzás, a ferritgyöngyök, a vezérlő második 24 V-os TVS-e (D7), az RGB-adatvonal soros ellenállása (R31) és a relémodul soros diódája (D100) kivéve). A lista a kapcsolási rajzok mostani állapotát írja le; a LED-modul NYÁK-ja huzalozva, a többi hátra van.

# 1. Modulmag (közös lap: a LED-, a relé- és a bemeneti modulon azonos)

## Táp a buszról

### Bemenet és 3,3 V-os stabilizátor

C2 (10 µF, kerámia): a buszról érkező 5 V puffere a modulnál – a kábel induktivitása miatti feszültségletörést és a bekapcsolási tüskéket simítja.

U5 (AP2112K-3.3, kis ejtésű lineáris stabilizátor): az 5 V-ból állítja elő a modul 3,3 V-os logikai tápját (mikrovezérlő, CAN-transceiver). Lineáris, mert kicsi a terhelés (~0,1 A), és nem zajos; kerámia kimeneti kondenzátorral is stabil.

C3 (10 µF, kerámia): a stabilizátor kimeneti kondenzátora – a szabályozó stabilitásához kötelező, és a terhelésugrásokat puffereli.

### A busz-feszültség mérése

R3, R4 (10 k / 10 k, 1 %): feszültségosztó, a busz 5 V-ját 2,5 V-ra osztja a mikrovezérlő ADC-jéhez (PC1, VBUS_SENSE). Így a modul jelezni tudja, ha a lánc végén túl kicsi a busz-feszültség (hosszú kábel, túlterhelés).

C9 (100 nF): az osztó szűrőkondenzátora – a zajt és a kapcsolási tüskéket szűri az ADC előtt.

### Hidegítés

C4–C8 (100 nF, 5 db): a mikrovezérlő egy-egy VDD-lábánál (1, 19, 32, 48, 64) – a nagyfrekvenciás áramimpulzusokat helyben szolgáltatják, a tápzajt szűrik.

C13 (4,7 µF): a 3,3 V-os sín közös puffer-kondenzátora a mikrovezérlő mellett (az ST ajánlása).


C14 (1 µF), C15 (10 nF): az analóg táp (VDDA) hidegítése a saját lábánál – a nagyobb a kisfrekvenciás, a kisebb a nagyfrekvenciás zajt viszi le. (Ferritgyöngy nincs: a hidegítő kondenzátorokkal csillapítatlan LC-kört alkotna, amely a rezonanciáján erősítené a zajt.)

## Mikrovezérlő

### U6 – STM32L433RCT3

U6 (STM32L433RCT3, Cortex-M4F, 80 MHz, 256 KB flash, LQFP64): a modul „agya” – a CAN-kommunikáció, a mérések (ADC) és a kimenetek vezérlése (PWM, GPIO) ezen fut. Az STM32F303RET6 helyére került: 75 db van belőle kézben, ugyanaz a CAN-periféria, és lábra kompatibilis (a relé- és a bemeneti modulon az F303 is beültethető).

### Órajel

Y1 (8 MHz kvarc): a mikrovezérlő pontos órajele. A CAN-kommunikációhoz pontos bitidő kell, a belső RC-oszcillátor ehhez nem elég pontos.

C10, C11 (12 pF): a kvarc terhelőkondenzátorai – a pontos rezgési frekvenciához kellenek, az értékük a kvarc adatlapjából (CL) számolódik.

### Reset és indítás

C16 (100 nF) + R6 (10 k felhúzás a 3,3 V-ra): az NRST láb szűrése és határozott magas szintje – a belső (~40 k-s) felhúzás mellett zavar ne okozzon véletlen újraindulást.

R2 (10 k): a BOOT0 láb lehúzása – bekapcsoláskor a mikrovezérlő a saját flash-éből indul (normál működés).

TP1 (mérőpont, BOOT0) és TP2 (mérőpont, 3V3): ha a kettőt bekapcsoláskor összekötjük, a gyári bootloader indul. A programozás alapvetően SWD-n (J1) történik; a gyári bootloader soros portjai nem a J1-en vannak, így ez csak tartalék.

### Debug és programozás

J1 (7 tűs tüskesor, DEBUG): programozás és hibakeresés SWD-n (ST-Link), mellette soros konzol (UART). Lábak: 3V3, SWCLK, GND, SWDIO, NRST, TX, RX.

### Állapot-LED-ek

D3 (zöld LED) + R8 (2,2 k): táp-LED – a busz 5 V-járól világít, jelzi, hogy a modul kap tápot. Azért az 5 V-ról, mert a kézben lévő zöld LED nyitófeszültsége ~3 V, a 3,3 V-ról alig világítana.

D4 (piros LED) + R9 (1 k): állapot-LED, a mikrovezérlő PC13 lába kapcsolja – a firmware ezzel jelez (működik, hiba, azonosítás).

### Revízió-azonosító (HW_REV)

A PB0 ADC-lábon egy feszültségosztó (10 k, 1 % + 715 Ω, 1 %, szűrő: 100 nF) a NYÁK-revíziót kódolja (16 feszültségsáv, a v1 az 1. sáv). Így a firmware tudja, melyik hardverváltozaton fut, ha később új revízió készül. Az osztó – a HW-ID-éhez hasonlóan – a modul saját lapján van (LED: R295/R296/C295, relé: R115/R116/C107, bemeneti: R303/R304/C308), mert a revízió az adott NYÁK tulajdonsága: egy modul új változatánál csak annak az ellenállása változik.

### Bővítő csatlakozó

J4 (2 × 5 tűs tüskesor, DNP): tartalék lábak kivezetése (SPI1, I²C1, egy GPIO) – később egy kiegészítő panel köthető rá forrasztás nélkül.

## CAN-busz

### Transceiver

U2 (CA-IS3052G, izolált CAN-transceiver): a mikrovezérlő logikai CAN-jeleit (TX/RX) alakítja át a busz differenciális jelévé (CAN_H/CAN_L) és vissza, a két oldal között galvanikus leválasztással (5 kVrms). A modul-oldala a +3,3 V-ról és a modul GND-jéről, a busz-oldala a busz 5 V-járól (V_BUS) és a busz földjéről (GND_BUS) jár. Buszlábai ±58 V-ot bírnak. Lábkompatibilis a TI ISO1042BDWVR-rel (az drágább alternatíva ugyanarra a helyre). A közös modulmag miatt mindhárom modulon ez van, de ténylegesen csak a LED-modulon választ le; a másik kettőn a két oldal össze van kötve.

C18 (100 nF), C19 (4,7 µF): a transceiver modul-oldali tápjának hidegítése.

C20 (100 nF), C21 (4,7 µF): a transceiver busz-oldali tápjának hidegítése (a CAN-meghajtó adáskor impulzusszerűen ~70 mA-t vesz fel).

R1 (10 k): a TX vonal felhúzása – bekapcsoláskor és reset alatt (amikor a mikrovezérlő lába még nem kimenet) a busz recesszív marad, a modul nem zavarja a többieket.

### Zavarszűrés

L1 (közös módusú CAN-fojtó, DNP): EMC-tartalék – ha a mérés közös módusú zavart mutat, beültethető.

JP2, JP3 (forrasztható áthidalók, alapból zárva): a fojtó helyét hidalják át; ha a fojtó bekerül, ezeket át kell vágni.

### Busz-csatlakozók és védelem

J2 (BUS_IN), J3 (BUS_OUT) (JST-XH, 4 tű): a lánc be- és kimenete, a tűk átmenők – így a modulok sorba fűzhetők.

U3 (ESD2CAN24-Q1): ESD-védelem a CAN-vonalakon – a csatlakozók érintésekor keletkező elektrosztatikus kisülést vezeti le.

D5 (SMF5.0A, TVS-dióda): az 5 V-os busz-tápot védi a bedugáskor (hot-plug) és ESD-nél fellépő tüskék ellen.

JP1 (jumper) + R5 (120 Ω): a CAN-busz lezárása – csak a lánc két végén lévő eszközön kell bekapcsolni, különben a jelvisszaverődés hibát okoz.

# 2. Vezérlő (ESP32-C6)

## Táp

### Bemenet és védelem (12–26 V)

J1 (2 pólusú csavaros sorkapocs, Degson DG128, 5,0 mm, 15 A): a 12–26 V-os betáp.

F1 (2 A biztosíték): zárlat esetén a tápot leválasztja (12 V-on és teljes 2 A-es buszterhelésnél a bemeneti áram ~1,2 A).

Q1 (IRFR1205, N-csatornás FET a GND-ágban) + R56 (10 k) + D12 (BZT52C15, 15 V-os Zener-dióda): fordított polaritás elleni védelem. Fordított bekötésnél a FET zár, így a táp + pólusa nem jut a lap GND-jére – ez a közös föld miatt fontos, mert különben a busz GND-erén át rövidzár alakulna ki. Helyes polaritásnál a FET teljesen nyitva van (elhanyagolható veszteség). A Zener a FET gate-jét a megengedett ±20 V alatt tartja. (Ez váltja ki a korábbi D1 soros Schottky-diódát.)

D2 (SMBJ28A, TVS): túlfeszültség-védelem a bemeneten (pl. a betápkábel induktivitása miatti tüskék).

R1 (150 k), R2 (10 k), C3 (100 nF): a bemeneti feszültség mérése (24 V → 1,5 V az ESP32 ADC-jére) – a firmware látja, ha a táp kiesik vagy alacsony.

TP1 (mérőpont, +24V_P): méréshez.

### 3,3 V (U1 LMR36015)

D8 (SS16, Schottky): a 24 V-os ágat köti a 3,3 V-os buck bemenetére, és megakadályozza, hogy az USB-táp visszatápláljon a 24 V-os oldalra.

D3 (SS56C, Schottky, 60 V / 5 A): USB-ről (24 V nélkül) is táplálja a 3,3 V-os buckot – így a vezérlő USB-ről önállóan is működik.

U1 (LMR36015, kapcsolóüzemű feszültségcsökkentő, 1 MHz): a 12–26 V-ból 3,3 V-ot állít elő az ESP32-nek, a W5500-nak és a LoRa-modulnak. Kapcsolóüzemű, mert lineáris stabilizátoron 24 V → 3,3 V-nál ~0,5 A-en több watt hő keletkezne.

C4 (10 µF / 50 V), C5, C6 (220 nF / 50 V): a buck bemeneti kondenzátorai – a kisebbek közvetlenül a VIN-lábaknál a nagyfrekvenciás kapcsolási áramot adják.

C7 (100 nF): bootstrap-kondenzátor – a buck felső kapcsolótranzisztorának gate-meghajtásához kell.

C8 (1 µF): a buck belső segédtápjának (VCC) kondenzátora.

L1 (6,8 µH, árnyékolt 0630-as tekercs, pl. SLO0630H6R8MTT): a buck energiatároló tekercse.

C10–C12 (22 µF, 3 db): a 3,3 V-os kimenet szűrése – a hullámosságot és a terhelésugrásokat (Wi-Fi-adás) kezelik.

R3 (100 k), R4 (43,2 k): visszacsatoló osztó – ez állítja be a 3,31 V-os kimenetet.

C9 (22 pF): előrecsatoló kondenzátor (CFF) – gyorsabb, stabilabb szabályozást ad.

TP3 (mérőpont, +3V3).

### 5 V (U2 LMR33630) – a busz tápja


C1 (47 µF / 50 V, elektrolit): kötelező csillapító kondenzátor – a betápkábel induktivitása és a kerámia-kondenzátorok rezgőkört alkotnak, és élő tápra kötéskor a feszültség túllőhet. A csillapítást az elkó ESR-je adja (~0,2–1 Ω a jó tartomány), ezért nem polimer vagy nagyon kis ESR-ű típus kell.

C2 (10 µF / 50 V), C53 (220 nF): a buck bemeneti kondenzátorai, a VIN-lábaknál.

U2 (LMR33630, kapcsolóüzemű feszültségcsökkentő, 3 A, 400 kHz): az 5,2 V-os busz-tápot állítja elő – ez táplálja az összes modul logikáját. ~2 A-re méretezve.

C54 (1 µF): a buck belső segédtápja (VCC).

C55 (100 nF): bootstrap-kondenzátor.

L3 (8,2 µH, árnyékolt 0630-as tekercs, pl. APS0630M8R2A, Isat ≥ 3,8 A): a buck energiatároló tekercse.

C56–C59 (22 µF, 4 db): az 5 V-os kimenet szűrése (a TI ajánlása szerint).

R54 (100 k), R55 (23,7 k): visszacsatoló osztó – 5,22 V-os kimenet.

D10 (SMBJ6.0A, TVS): ha a buck meghibásodik és átüt (24 V jelenne meg a kimenetén), rövidre zár és kiolvasztja az F1-et – így a buszra nem jut 24 V.

### USB vagy buck (U12 LM66200)

U12 (LM66200, kettős ideális dióda): az 5 V-os buckot és az USB 5 V-ját „VAGY”-kapcsolja: mindig a nagyobb feszültségű forrás táplál, és egyik sem táplál vissza a másikba. Így USB-ről is működik a busz (1–2 modul teszteléséhez 24 V nélkül).

C13 (22 µF), C22 (1 µF), C23 (100 nF): az összevont +5V sín pufferei.

TP2 (mérőpont, +5V).

### A busz kapcsolása és védelme (U3 TPS2595 eFuse)

U3 (TPS259531, elektronikus biztosíték): a buszra menő 5 V-ot kapcsolja és védi – 2 A-nél korlátoz, 5,7 V felett lekapcsol, lágyan indít. Egy modul zárlata így nem viszi le a vezérlőt.

R10 (100 k), R11 (47 k): az eFuse engedélyező osztója a +5V-ról – bármelyik tápforrásról magától bekapcsol.

D9 (BAT54HT1G, Schottky): a GPIO20 ezen át le tudja húzni az engedélyező lábat – a firmware szoftveresen lekapcsolhatja a buszt (pl. hibánál újraindításhoz).

C60 (22 nF): a felfutási sebességet állítja be (~2,7 ms) – így a modulok kondenzátorai nem okoznak nagy bekapcsolási áramlökést.

R12 (1,02 k, 1 %): az áramkorlát beállítása (2,0 A).

R34 (10 k): a hibajelző kimenet (FLT, nyitott drain) felhúzása – a GPIO21 látja, ha az eFuse lekapcsolt.

C24 (100 nF), C25 (10 µF): a busz-kimenet (V_BUS) pufferei.

D4 (SMF5.0A, TVS): a busz 5 V-ját védi a kábelen érkező tüskék ellen.

R13 (100 k), R14 (22 k), C14 (100 nF): a busz-feszültség mérése (5 V → 0,9 V a GPIO1-re).

TP4 (mérőpont, V_BUS).

## ESP32-C6

U4 (ESP32-C6-WROOM-1-N8, 8 MB flash): a vezérlő processzora rádiókkal (Wi-Fi, Thread/802.15.4, BLE) – Matter-hídként kapcsolja össze a modulokat a Home Assistanttel.

C26 (22 µF), C27 (100 nF): a modul 3,3 V-os lábának hidegítése (a Wi-Fi-adás impulzusszerű áramot vesz).

R15 (10 k), C15 (1 µF): RC-késleltetés az EN (engedélyező) lábon – a chip csak a táp stabilizálódása után indul (Espressif-ajánlás).

SW1 (RESET nyomógomb): újraindítás (az EN-t a GND-re húzza).

SW2 (BOOT nyomógomb): a GPIO9-et lehúzva letöltő módban indul (firmware-feltöltés).

R16 (10 k): a BOOT (GPIO9) felhúzása – normál indulás.

R17 (10 k): a GPIO8 felhúzása – indításkor ennek 1-nek kell lennie (strapping-láb), és ugyanez a láb hajtja az RGB LED-et.

R18 (10 k): a GPIO15 felhúzása (strapping-láb, meghatározott indulási állapot).

R35 (10 k): a CAN TX felhúzása – reset alatt a busz recesszív marad.

R19 (0 Ω), C28 (DNP): az SPI órajel soros eleme – ha a jelélek túl meredekek (zavar), 33 Ω és kondenzátor tehető a helyére.

R39 (499 Ω): soros ellenállás a debug-UART TX vonalán (Espressif-ajánlás).

J5 (6 tűs tüskesor, DEBUG): soros konzol és programozás USB-UART adapterrel (VREF, GND, TX, RX, EN, BOOT).

R33 (0 Ω, DNP): a J5 referenciatápja – alapból nincs beültetve, hogy a soros adapter ne táplálja vissza a lapot.

## Ethernet (opcionálisan beültetve)

U5 (W5500, Ethernet-vezérlő SPI-n): az ESP32-C6-ban nincs Ethernet-MAC, ezért egy külső chip adja a vezetékes hálózatot (Thread mellett is használható).

Y1 (25 MHz kvarc, CL = 10 pF, ESR ≤ 30 Ω), C40, C41 (12 pF): a W5500 órajele és terhelőkondenzátorai – a kondenzátor értéke a kvarc terhelő kapacitásából: C = 2 × (CL − 3…5 pF).

R47 (1 M, DNP): a kvarccal párhuzamos ellenállás a WIZnet-referencia szerint – alapból nem kell.

R40 (12,4 k, 1 %): a PHY belső áramreferenciája (EXRES) – az adatlap előírt értéke.

C29 (4,7 µF), C30 (10 nF): a W5500 belső 1,2 V-os stabilizátorának kondenzátorai (TOCAP, 1V2O).

R48–R50 (DNP): a PHY üzemmódját rögzítő lehúzások – nyitva auto-negotiation (a gép maga egyezteti a sebességet).

R36, R37, R38 (10 k): a W5500 CS, RST és INT vonalainak felhúzása – meghatározott állapot indításkor (a chip ne válaszoljon véletlenül a közös SPI-buszon).


C31–C36 (100 nF, 6 db): az analóg táplábak (AVDD) hidegítése, lábanként.

C37 (100 nF): a digitális tápláb (VDD) hidegítése.

C38, C39 (10 µF): a 3,3 V-os és az analóg sín puffere.

R20–R23 (49,9 Ω, 1 %): az Ethernet-vonalak illesztő lezárása (a 100 Ω-os kábelimpedanciához) – a WIZnet-referencia szerint.

C16 (10 nF): a TX-lezárás közös pontjának hidegítése.

C17 (10 nF): az RX-lezárás közös pontja (RCT) a GND felé.

C19, C61 (6,8 nF): soros kondenzátorok az RX-vonalakban (a WIZnet-referencia szerint, egyenáramú leválasztás).

J6 (HR911105A, RJ45 aljzat beépített transzformátorral): a hálózati csatlakozó; a transzformátor galvanikusan leválasztja a kábelt.

R24 (10 Ω), C18 (22 nF): a transzformátor középleágazásának (TCT) táplálása és szűrése.

C20 (1 nF / 2 kV): az aljzat árnyékolását és a nem használt érpárok lezárását köti a GND-re – nagyfeszültségű tüskéknél is bírja.

R41, R42 (330 Ω): az aljzatba épített link- (zöld) és aktivitás- (sárga) LED áramkorlátozói.

## USB-C

J4 (USB-C aljzat): táp és programozás/konzol (az ESP32-C6 beépített USB-jén).

R28, R29 (5,1 k): a CC-vonalak lehúzása – ezzel jelzi a töltőnek, hogy 5 V-ot kér (USB-C táp-fogyasztó).

U8 (USBLC6-2SC6): ESD-védelem az USB adatvonalain.

R26, R27 (22 Ω): soros ellenállások a D+/D− vonalakon az ESP32 mellett (jelillesztés, Espressif-ajánlás).

C49, C50 (DNP): kondenzátorhely az adatvonalakon, ha EMC miatt kellene.

D11 (SMF5.0A, TVS): az USB 5 V-ját védi a bedugási túllövés ellen (az LM66200 bemenete max. 6 V-ot bír).

R30 (2,2 k): levezető ellenállás – kihúzott USB-nél a D3 szivárgása ne tartsa „élve” a VUSB-t.

C21 (1 µF): a VUSB puffere.

## CAN

U6 (TCAN1044AV, CAN-transceiver, ±58 V-os buszlábak): a vezérlő CAN-jeleit alakítja a busz jelévé. A footprintre jumperekkel más típus (pl. SN65HVD230) is beültethető.

JP2 (3 padas jumper, VCC: 5 V / 3,3 V), JP3 (VIO: 3,3 V / GND): a transceiver tápjának kiválasztása az éppen beültetett típushoz.

C42 (100 nF), C43 (1 µF): a transceiver tápjának hidegítése.

C44 (100 nF): az I/O-táp (VIO) hidegítése.

R43 (0 Ω): a készenléti láb (STB) a GND-re – normál üzemmód.

L2 (közös módusú fojtó, DNP) + JP4, JP5 (áthidalók): EMC-tartalék, mint a modulokon.

U7 (ESD2CAN24-Q1): ESD-védelem a CAN-vonalakon.

JP1 (jumper) + R25 (120 Ω): a busz lezárása (a lánc elején a vezérlő a természetes vég).

J2, J3 (JST-XH, 4 tű): a busz két kimenete.

TP5, TP6, TP7 (mérőpontok: CAN_H, CAN_L, GND): oszcilloszkópos méréshez.

## LoRa (előkészítés, DNP)

U10 (Ebyte E22-900M22S, 868 MHz-es LoRa-modul, DNP): későbbi nagy hatótávú, elemes érzékelőkhöz – most nincs beültetve.

U11 (74LVC1G04, inverter, DNP): a modul antennakapcsolójának vezérlése (vétel = az adás-jel negáltja).

R46 (0 Ω, DNP): a LoRa-modul tápjának leválasztó pontja – áramméréshez is.

C51 (10 µF), C52 (100 nF) (DNP): a LoRa-modul tápjának hidegítése.

R51 (10 k, DNP): a LoRa SPI-chipválasztójának felhúzása.

J7 (u.FL csatlakozó, DNP): antenna-csatlakozó (pigtail a ház SMA-aljzatához).

## Visszajelzés

D5 (zöld LED) + R44 (2,2 k): táp-LED (a +5V-ról, mint a modulokon).

D6 (WS2812B-V5, címezhető RGB LED): állapotjelző (pl. párosítás, hálózat, hiba) – egy adatvezetéken vezérelhető színes LED.

U9 (74HCT14, Schmitt-triggeres inverter): szintillesztő – az ESP32 3,3 V-os jelét 5 V-os szintre emeli a WS2812-nek (két inverter sorban, így a jel nem fordul meg).


R32 (0 Ω, DNP): áthidalja a szintillesztőt, ha az nincs beültetve (3,3 V-os bemenetű LED-nél).

C45, C46 (100 nF): az U9 és a D6 tápjának hidegítése.

## Bővítő csatlakozó

J8 (JST-PH, 3 tű: 3V3, GPIO5, GND): egy külső érzékelő (pl. 1-wire hőmérő) csatlakozója.

R52 (4,7 k, DNP): felhúzás 1-wire érzékelőhöz.

R53 (DNP): lehúzás vagy osztó alsó tagja, ha analóg jel jön.

# 3. LED-modul (6 csatorna × 10 A, összesen 15 A)

## Modulmag

A mikrovezérlő, a busz-táp és a CAN a modulmag fejezetben (1.) van leírva. Lábkiosztás ezen a modulon: CH1–CH3 PWM a TIM1-ről (PA8–PA10), CH4–CH6 a TIM15/TIM16-ról (PB14, PB15, PB8), áram-mérés a PA3-on.

## Azonosítás és mérés

R201 (10 k, 1 %), R202 (715 Ω, 1 %), C201 (100 nF): HW-ID – a feszültségosztó kódolja a modul típusát (LED = 1. sáv). Mivel a modulmag minden modulon azonos, a firmware ebből tudja, milyen modulon fut, és ennek megfelelően kezeli a kimeneteket (pl. nem kapcsol relékimenetet egy LED-modulon).

R295 (10 k, 1 %), R296 (715 Ω, 1 %), C295 (100 nF): HW_REV – a LED-modul NYÁK-revíziója (v1 = 1. sáv), lásd a modulmagnál.

R290 (150 k), R291 (10 k), C290 (100 nF): a bejövő 12–26 V mérése a főbiztosíték előtt (24 V → 1,5 V a PB1-re) – a firmware ellenőrzi, hogy van-e táp, és hogy a szalag feszültségéhez illik-e.

U208 (B0505S-1WR3, 1 W-os izolált DC-DC, 5 V → 5 V): a modul logikájának tápja a busz 5 V-járól, galvanikus leválasztással. Így a LED-modul földje és a busz földje között nincs közvetlen kapcsolat: ha a betáp GND-vezetéke működés közben leesik, a szalag árama nem tud a buszon át visszafolyni – a szalag egyszerűen kialszik. A modul ~50–100 mA-t vesz fel, a konverter 200 mA-t bír. Ugyanerre a helyre a 12 V-os vagy 24 V-os bemenetű változat (B1205S, B2405S) is beültethető, ha a busz feszültsége egyszer változna.

C216 (4,7 µF), C217 (10 µF): a DC-DC bemeneti (busz-oldali) és kimeneti (modul-oldali) kondenzátora.

C218 (2,2 nF / 1 kV, DNP): a két föld közötti EMC-kondenzátor helye – ha a mérés a DC-DC kapcsolási zaját mutatja a buszon, beültethető.

## Betáp és a 24 V-os sín

J201 (2 pólusú csavaros sorkapocs, Degson DG128, 15 A UL / 18 A IEC): a LED-szalagok 12–26 V-os betápja – a modul össz-árama ehhez igazodik (15 A).

F201 (15 A, NANO² SMD biztosíték, beforrasztva): a teljes modul főbiztosítéka – zárlatnál leválasztja a tápot.

Q201 (NCEP6090AGU, N-csatornás FET a GND-ágban, ~2,8 mΩ) + R294 (10 k) + D202 (BZT52C15, 15 V-os Zener): fordított polaritás elleni védelem. Fordított bekötésnél a FET zár, így a +24 V nem jut a lap GND-jére, és a közös földön (busz) át sem alakul ki zárlat. Helyes polaritásnál a FET nyitva van: a legnagyobb, 15 A-es áramnál ~42 mV esik rajta (~0,6 W). Az R294 a gate-et a 24 V-os sínről nyitja, a Zener a gate-feszültséget 15 V-ra korlátozza. (Ez váltja ki a korábbi ideális diódát, az LM74700-at.)

D201 (SMBJ28A, TVS): túlfeszültség-védelem a sínen (pl. a szalagkábelek induktivitásából eredő tüskék).

C203 (470 µF / 50 V, elektrolit): a sín fő puffere – a PWM-kapcsolás nagy áramimpulzusait helyben szolgáltatja, és csillapítja a betápkábelen a lengést.

C204–C206 (10 µF / 50 V, kerámia): nagyfrekvenciás pufferek közvetlenül a FET-ek mellett.

R203 (100 k), R204 (10 k), C207 (100 nF): a sín feszültségének mérése a biztosíték után (PC2) – a VIN_SENSE-szel összevetve kiderül, ha az F201 kiolvadt.

## 12 V-os gate-táp

U205 (MC78L12, 12 V-os lineáris stabilizátor): a gate-meghajtók tápja – a FET-ek gate-jét 12 V-tal kell nyitni a kis veszteséghez; lineáris, mert csak néhány mA kell.

C208 (1 µF / 50 V), C209 (10 µF / 25 V): a stabilizátor be- és kimeneti kondenzátora.

## Gate-meghajtók

U201–U203 (UCC27524, kettős gate-meghajtó, 4 A): a mikrovezérlő 3,3 V-os PWM-jeleit erősítik fel a FET-ek gyors kapcsolásához (a nagy gate-kapacitást gyorsan kell tölteni, különben a FET a kapcsolás alatt melegszik). Három tok, egyenként két csatorna.

C210, C212, C214 (1 µF) és C211, C213, C215 (100 nF): a meghajtók tápjának hidegítése, tokonként.

R205 (1 k): a közös engedélyező vonal (DRV_EN, PB12) lehúzása – bekapcsoláskor, amíg a mikrovezérlő nem fut, minden csatorna biztosan KI van.

## Kimeneti blokkok

F202–F204 (NANO² SMD biztosíték, a szalaghoz méretezve: ≤ 100 W-os ághoz 4 A, legfeljebb 10 A): blokkonként (2 csatornánként) külön biztosíték – egy szalag zárlata nem viszi le a többit, és a kis ágbiztosíték a vékonyabb szalagvezetéket is védi.

J202–J204 (3 pólusú csavaros sorkapocs, KF128, 10 A): a kimenetek – blokkonként +24 V, CHa, CHb (pl. egy CCT-szalag két színe).

## Csatornák (× 6)

Q202–Q207 (NCE6080K, 60 V-os N-csatornás FET, ~8,5 mΩ, DPAK): az alsó oldali kapcsolók – a szalag negatív vezetékét kapcsolják a GND-re PWM-mel (fényerő-szabályozás, 25 kHz).

R211–R216 (10 Ω): gate-ellenállások – lassítják a kapcsolási élt (kisebb EMC-zavar, csillapítják a gate-kör lengését).

R221–R226 (10 k): gate–source lehúzások – ha a meghajtó nem kap tápot, a FET biztosan zárva marad.

D211–D216 (SS56B, Schottky, 5 A / 60 V): szabadonfutó diódák a szalag két vége között – a kábel induktivitásából kikapcsoláskor keletkező feszültségtüskét elvezetik, így az nem üti át a FET-et.

R231–R236 (10 Ω) + C221–C226 (2,2 nF) (DNP): RC-snubber a drainen – csak akkor kerül be, ha a mérés kapcsolási lengést mutat.

R241–R246 (10 k) + D221–D226 (zöld LED): gate-LED-ek – azt mutatják, hogy a mikrovezérlő bekapcsolta a csatornát.

R251–R256 (10 k) + D231–D236 (zöld LED): drain-LED-ek – azt mutatják, hogy a kimenet ténylegesen kapcsol (a gate- és a drain-LED összevetéséből a hiba látszik, pl. kiolvadt blokk-biztosíték).

R261–R266 (470 k), R271–R276 (56 k), C231–C236 (10 nF): drain-feszültség mérése (24 V → 2,55 V az ADC-re) – önteszthez: kikapcsolt állapotban kiderül, van-e szalag a kimeneten, kiolvadt-e a biztosíték, illetve átütött-e a FET.

## Össz-áram és túláram-védelem

R209 (1 mΩ, 2512, 3 W söntellenállás, Kelvin-bekötésű footprinten): a hat csatorna közös visszatérő áramát méri (15 A-en 15 mV).

U206 (INA181A2, áramérzékelő erősítő, ×50): a sönt kis feszültségét 0–1 V-ra erősíti (20 A → 1,0 V).

C240 (100 nF): az erősítő tápjának hidegítése.

R207 (1 kΩ), C241 (1 nF): RC-tag az erősítő kimenetén – leválasztja az erősítőt a kapacitív terheléstől (az INA181 közvetlenül legfeljebb 1 nF-ot bír), töltést ad az ADC mintavevőjének, és ~160 kHz fölött levágja a zajt; a komparátort csak ~1 µs-mal lassítja.

A túláram-lekapcsolás hardveres: a mért jel (I_SENSE, PA3) a mikrovezérlő belső komparátorára megy, amelynek küszöbét a belső DAC (PA4) adja; túllépéskor a komparátor közvetlenül leállítja mind a hat PWM-et (timer break), szoftver közreműködése nélkül, mikroszekundumok alatt.

TP202 (mérőpont, I_SENSE), TP201 (mérőpont, DAC_THR): a mért áram és a beállított küszöb ellenőrzéséhez.

## Hőmérséklet

U207 (MCP9701A, analóg hőmérő, 19,5 mV/°C) a FET-ek között: a teljesítményrész hőmérsékletét méri (PC3) – túlmelegedésnél a firmware csökkenti a terhelést vagy lekapcsol (harmadik védelmi réteg a biztosítékok és a túláram-védelem mögött). Lineáris kimenetű, így nem kell hozzá táblázat. (A korábbi NTC-termisztor helyére került.)

C243 (100 nF): a hőmérő tápjának hidegítése.

R208 (200 Ω), C242 (100 nF): szűrő a hőmérő kimenetén – a soros ellenállás azért kell, mert a hőmérő kimenete nagy kapacitív terhelést közvetlenül nem bír.

# 4. Relémodul (4 × 16 A, 230 V)

## Modulmag

A mikrovezérlő, a busz-táp és a CAN a modulmag fejezetben (1.) van leírva. Ezen a modulon a relék a PB12–PB15 lábakon, a tekercs-feszültség mérése a PB1-en van.

## Azonosítás és mérés

R101 (10 k, 1 %), R102 (1,54 k, 1 %), C101 (100 nF): HW-ID – relémodul 24 V-os tekercsekkel = 2. sáv (12 V-os relékkel R102 = 3,65 k → 4. sáv). A firmware így tudja, milyen relék vannak beültetve.

R115 (10 k, 1 %), R116 (715 Ω, 1 %), C107 (100 nF): HW_REV – a relémodul NYÁK-revíziója (v1 = 1. sáv).

R111 (150 k), R112 (10 k), C106 (100 nF): a tekercs-táp mérése (PB1) – a firmware összeveti a HW-ID-vel, és letiltja a kapcsolást, ha pl. 24 V-os relék mellett csak 12 V a táp (a relé nem húzna be megbízhatóan).

R113 (0 Ω, 1206): a busz GND-ér és a modul GND-je közötti kapcsolat – a relémodul nincs leválasztva a busztól (a tekercsek árama kicsi).

R100 (0 Ω, 1206): a busz 5 V-ja (V_BUS) és a modul +5 V-ja közötti átkötés – a LED-modulon ennek a helyén izolált DC-DC van.

U100 (B0505S-1WR3, DNP) + C100 (4,7 µF), C108 (10 µF), C109 (2,2 nF / 1 kV): az izolált DC-DC helye, mint a LED-modulon. Ha a relémodult is le kell választani a busztól, az R100 és az R113 helyett ezek kerülnek be (a kettő együtt nem).

## Betáp és tekercs-táp

J100 (2 pólusú csavaros sorkapocs, Degson DG128): a 12–26 V-os betáp (csak a relétekercseknek, kis áram).

Q100 (IRFR120N, N-csatornás FET a GND-ágban) + R114 (10 k) + D106 (BZT52C15, 15 V-os Zener-dióda): fordított polaritás elleni védelem a közös föld miatt, mint a vezérlőn és a LED-modulon.

F100 (0,5 A biztosíték): a tekercs-táp védelme (4 tekercs × ~17 mA).


D105 (SMBJ28A, TVS): túlfeszültség-védelem.

C104 (10 µF / 50 V, kerámia), C105 (47 µF / 50 V, elektrolit): a tekercs-táp pufferei – az elektrolit a betápkábel lengését csillapítja.

## Relék és meghajtás

U101 (ULN2803A, 8 csatornás Darlington-tranzisztorsor): a mikrovezérlő 3,3 V-os kimenetei ezen át kapcsolják a 24 V-os relétekercseket; a beépített diódák elvezetik a tekercs kikapcsolásakor keletkező feszültségtüskét. Bekapcsoláskor (lebegő bemenet) a kimenetek KI vannak.

K1–K4 (Schrack RTD14024, 16 A-es, 24 V-os relé): a 230 V-os terhelések kapcsolása, galvanikus leválasztással.

R103–R106 (10 k) + D101–D104 (zöld LED): relé-állapot LED-ek – akkor világítanak, ha az adott tekercs be van kapcsolva (az előlapon, fényvezető alatt).

## 230 V-os kimenetek

J101–J104 (2 pólusú, 5,08 mm-es THT sorkapocs, COM + NO, ≥ 16 A, ≥ 250 V): a relék kimenetei. A 230 V-os rész a NYÁK-on ≥ 8 mm-re van a törpefeszültségű résztől, a belső rétegeken alatta nincs réz.

## Fogyasztásmérés-előkészítés (DNP)

J105 (3,5 mm-es jack, SCT-013 lakatfogós áramváltóhoz, DNP): egy kimenet áramának mérése (v2-ötlet); a lakatfogó leválaszt, a 230 V-os oldalt nem érinti.

R107, R108 (10 k / 10 k) + C102: 1,65 V-os középfeszültség – az áramváltó váltakozó jelét az ADC tartományának közepére emeli.

R109 (terhelő-ellenállás): csak áramkimenetes áramváltóhoz kell.

R110 (1 k), C103 (10 nF): soros ellenállás és szűrő az ADC (PA0) előtt.

# 5. Bemeneti modul (16 bemenet + klíma-érzékelő)

## Modulmag

A mikrovezérlő, a busz-táp és a CAN a modulmag fejezetben (1.) van leírva. A 16 bemenet a PA0–PA10 és a PB11–PB15 lábakon van, mindegyik külön megszakítás-vonalon.

## Azonosítás

R301 (10 k, 1 %), R302 (2,49 k, 1 %), C301 (100 nF): HW-ID – bemeneti modul = 3. sáv.

R303 (10 k, 1 %), R304 (715 Ω, 1 %), C308 (100 nF): HW_REV – a bemeneti modul NYÁK-revíziója (v1 = 1. sáv).

R390 (0 Ω, 1206): a busz GND-ér és a modul GND-je – itt 0 Ω, mert a modul teljesen a buszról jár (nincs saját betápja), ellenállás itt nem lehet.

R300 (0 Ω, 1206): a busz 5 V-ja (V_BUS) és a modul +5 V-ja közötti átkötés – az érzékelők tápja is ezen megy (≤ ~1 A).

U300 (B0505S-1WR3, DNP) + C300 (4,7 µF), C309 (10 µF), C326 (2,2 nF / 1 kV): az izolált DC-DC helye. Leválasztáshoz az R300 és az R390 helyett ezek kerülnek be – ilyenkor a DC-DC ~200 mA-jéből az érzékelőknek ~100 mA marad.

## Érzékelő-táp

C302 (10 µF): a busz 5 V-jának puffere az érzékelő-táp stabilizátoránál.

U301 (AP2112K-3.3, kis ejtésű lineáris stabilizátor): külön 3,3 V-os sín (+3V3S) a külső érzékelőknek – egy hibás érzékelő így nem húzza le a mikrovezérlő tápját. A kis tok miatt összesen néhány száz mA-es érzékelőterhelésre való (5 V → 3,3 V-nál a különbség hővé alakul).

C303 (10 µF, kerámia): a stabilizátor kimeneti kondenzátora.

JP301–JP304 (3 padas jumper): a négy érzékelőcsoport tápjának kiválasztása (3,3 V vagy 5 V) – csoportonként 4 bemenet.

F301–F304 (PTC, 0,2 A, visszaálló biztosíték): csoportonként – egy zárlatos érzékelő-kábel csak a saját csoportját kapcsolja le, és a hiba megszűnése után magától visszaáll.

C304–C307 (1 µF): a csoport-tápok pufferei.

## Bemenetek (× 16)

J301–J316 (JST-PH, 3 tű: táp, GND, jel): bemenetenként egy csatlakozó – kapcsoló, reed-relé, Hall-érzékelő vagy más digitális jel köthető rá.

R330–R345 (10 k): felhúzó ellenállások a csatlakozó oldalán – nyitott kontaktusnál a bemenet 1, zártnál 0 (kontaktus-érzékelőkhöz nem kell külső ellenállás). 12/24 V-os jelnél kivehető.

R310–R325 (10 k, soros): áramkorlát a mikrovezérlő lába előtt – ha valaki tévedésből 24 V-ot köt egy osztó nélküli bemenetre, legfeljebb ~2 mA folyik, és ezt az ESD-védő tömb (U303–U306) veszi fel. A láb feszültsége ekkor az ESD-tömb letörési feszültségére áll be, ami a mikrovezérlő 5 V-tűrő lábának határa (~7,3 V) körül van – ez csak félrekötés elleni tartalék, 12/24 V-os jelhez az osztót be kell ültetni.

R350–R365 (DNP): feszültségosztó alsó tagja – 5/12/24 V-os jelhez beültethető (akkor a soros ellenállás 68 k).

C310–C325 (10 nF): aluláteresztő szűrő – a kontaktuspergést és a kábelen összeszedett zavart szűri.

U303–U306 (TPD4E05U06, 4 csatornás ESD-védő): az ESD-tüskéket vezetik le a bemeneteken, tokonként 4 bemenet.

## Klíma-érzékelő és külső I²C

U302 (HDC3020, hőmérséklet- és páratartalom-érzékelő, I²C): a ház belsejének (elosztószekrény) klímáját méri – a szoba klímájához a külső I²C-érzékelő való. A NYÁK szélén van, a melegedő részektől távol.

C330 (100 nF): az érzékelő tápjának hidegítése.

R371, R372 (4,7 k): az I²C-busz (SCL, SDA) felhúzó ellenállásai.

R373 (10 k): az érzékelő riasztás-kimenetének (ALERT) felhúzása.

J320 (JST-PH, 4 tű: táp, GND, SDA, SCL): külső I²C-érzékelő csatlakozója (kábel ≤ 2 m, 100 kHz).

F305 (PTC, 0,2 A): a külső érzékelő tápjának védelme.

R374, R375 (100 Ω): soros ellenállások a külső I²C-vonalakon – a kábelen érkező tüskék és a reflexió ellen.

U307 (TPD4E05U06): ESD-védelem a külső I²C-csatlakozón.
