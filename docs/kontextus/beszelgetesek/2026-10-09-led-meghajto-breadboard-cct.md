# 24 V LED-meghajtó breadboard és CCT szalag – 2026-10-09/10

Forrás: claude.ai „szakdolgozat” Projekt, a „Matter hálózat csatlakozás” chat második fele
(2026-10-09 délután – 2026-10-10 este). Balázs a breadboardon dolgozott, Claude a felhőből tervezett.

## Alkatrészek a LED-meghajtáshoz
- **FDP2532** (onsemi): N-FET, 150 V, 79 A, 16 mΩ @ 10 V, TO-220, lábak G-D-S, a fül a drain. Nem logic-level,
  3,3 V-os GPIO-ról nem nyit ki rendesen.
- **IRFP064N:** 55 V, kb. 110 A, 8 mΩ @ 10 V, TO-247 (nem fér a breadboardba), nagyobb gate-töltés. Csak driverrel,
  nagy áramhoz.
- **NE556-os 12 V-os panel 24 V-ra:** az 556 elé 78L12, az IRL3713 (30 V) helyére FDP2532.

## Breadboard kapcsolás (Rev A, csatornánként azonos)
- GPIO → R1 1k → T1 (BC546B) bázis; R2 4,7k bázis–GND; T1 emitter GND.
- R3 47k +24 V → T1 kollektor / T2 bázis. T2 emitter GND, kollektor → gate.
- R4/R5 4,7k osztó (+24 V → gate → GND) → kb. 12 V gate. Q1 FDP2532 low-side, drain → a szalag „–” vezetéke.
- Nem invertál (GPIO HIGH = BE). Bootkor, reset alatt és USB nélkül is KI: az R2 legyőzi a GPIO18–23 resetkori
  kb. 45 kΩ-os belső felhúzását.
- PWM legfeljebb kb. 1 kHz: a gate 2,35 kΩ-on töltődik, a teljes bekapcsolás 25–30 µs.
- Csatornák: GPIO20 és GPIO21, közös +24 V és GND. Két bekötési hibát feszültségméréssel megtaláltunk és javítottunk.
- Mért értékek (GND-hez képest):

| Állapot | T1 B | T1 C | T2 C | Gate |
|---|---|---|---|---|
| KI | – | ≈ 0,7 V | ≈ 0,05 V | ≈ 0,05 V |
| BE | ≈ 0,7 V | ≈ 0,05–0,1 V | ≈ 12 V | ≈ 12 V |

- Kapcsolási rajz (egycsatornás Rev A): https://claude.ai/artifact/6WBn3Wgx1kgkpAMme6vWLG

## 20 kHz feletti PWM
- A tranzisztoros fokozattal nem megy: 25 kHz-en a FET az idő nagy részében félig nyitva lenne, egy kb. 2 A-es
  szalaggal is kb. 5 W kapcsolási veszteség. Megoldás: TC4427 gate driver 12 V-ról (78L12), 25 kHz-en kb. 0,1–0,2 W.
- **PCA9685** (I²C, 16 csatorna, 12 bit): legfeljebb kb. 1,5 kHz, ezért 20 kHz felett nem jó. Sok csatornához
  1 kHz körül használható. VCC 3,3 V-ról; a V+ sorkapocsra nem mehet 24 V.

## CCT szalag (Balázs válaszai, 2026-10-10)
- Egy CCT szalag a két csatornán: GPIO20 = meleg, GPIO21 = hideg (nem végleges).
- 3000 K / 6000 K, 16 W/m, 18 m, 24 V; táp 24 V / 15 A.
- Matter: Color Temperature Light. Keverés: maximális fényerő (középen mindkét csatorna 100 %). Áramszünet után KI.
  0,5 s átmenet. BOOT: egy kattintás ki/be, dupla kattintás meleg → semleges → hideg. A board RGB LED-je
  állapotjelző lesz.
- Terhelés: 288 W ≈ 12 A, ha a 16 W/m a két szín együtt (nyitott kérdés; ha színenként, `CCT_MAX_SUM = 1.0`).
  Breadboardon legfeljebb 1–2 m szalag; a teljesítményág le a breadboardról, vastag vezeték, hűtőborda a FET-eken.
  A 18 m-hez több betáplálási pont kell (egy végről kb. 5 m, legfeljebb 10 m).
- Claude Code prompt készült a CCT firmware-re (endpoint 1 = Color Temperature Light, LEDC 1 kHz, gamma 2,2,
  min. 3 % kitöltés, `CCT_MAX_SUM`, állapotjelző RGB LED). A repóban még nincs nyoma. A node/modul architektúra
  (lásd a 2026-10-10-i jegyzetet) óta ez a breadboardos prototípushoz érvényes.
