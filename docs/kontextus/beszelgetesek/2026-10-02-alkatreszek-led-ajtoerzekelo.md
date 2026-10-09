# Alkatrészek: LED-meghajtás, ajtóérzékelő – 2026-10-02/03

Forrás: claude.ai chat „MOSFET-ek és ajtóérzékelő modul”
(https://claude.ai/chat/8f0f8c04-177d-4d3b-bf2d-87d7dd818d99).

## LED-szalag meghajtás
- **IRFP064N, FDP2532:** nem logic-level FET-ek (Vgs(th) 2–4 V, az Rds(on)-t 10 V-on adják meg). 3,3 V-os GPIO-ról
  nem nyitnak ki rendesen, és LED-szalaghoz túlméretezettek (nagy, ~100–170 nC gate-töltés).
  - Ha mégis ezek kellenek: **NPN szintillesztő** (GPIO → 1 kΩ → BC546/2N3904, a gate 1 kΩ-mal 12 V-ra felhúzva),
    ~1 kHz PWM-ig jó. Gyorsabb változat: BC847B/BC857B push-pull fokozat ~10 Ω-mal a gate-re. Rendes megoldás:
    **TC4427 / MCP1416** gate driver.
  - Az NPN-es szintillesztő **invertál, és boot alatt bekapcsolja a LED-et**. Ez ellen egy plusz NPN fokozat vagy
    nem invertáló driver lehúzott bemenettel. (ESPHome-ban `inverted: true`, de a boot alatti felvillanást ez
    nem szünteti meg.)
- **Új tervhez:** logic-level FET, pl. **AO3400A** (12 V). 24 V-hoz legalább 40 V-os FET. GPIO → ~100 Ω → gate,
  gate–source között 100 kΩ.
- **Gate max ±20 V:** a 24 V-os sínről 12 V-os ág vagy ~15 V-os zener kell.
- Lábkiosztás: BC546 = C-B-E, 2N3904 = E-B-C (fordított!). Ne keverd egy footprinten.

## 12 V-os LED-vezérlő panel (NE556 + IRL3713) 24 V-ra
- Az **NE556** max. 16 V → 24 V-on tönkremegy. Elé **78L12** kell, ami a FET gate-jét is 12 V alatt tartja.
- Az **IRL3713** 30 V-os, 24 V-hoz kevés a tartalék → helyette a kézben lévő **FDP2532** (azonos TO-220 lábkiosztás).
- Nyitott: van-e már stabilizátor a panelen (a fekete, fém fülű alkatrész)? A szalagnak is 24 V-osnak kell lennie.

## Ajtóérzékelés
- **Lézeres közelítésérzékelő (Waveshare-klón, 12 db):** 2,5–5 V, ~40 mA, 650 nm, a DOUT a VCC-re van felhúzva,
  tárgy előtte = LOW, 0,01–0,8 m. Ajtóhoz nem ideális (folyamatos fogyasztás, nyitott ajtónál kifelé világít).
  Jó lehet: lépcső, áthaladás-irány, garázs, postaláda, szintjelzés. Sok darabot TCA9554 bemenetre kötni (5 V-tűrő).
- **AH1911 Hall-kapcsoló (5 db) – ezt választottuk:** 1,6–5,5 V, ~1,6 µA, omnipoláris, push-pull kimenet
  (nem kell felhúzás), mágnesnél LOW = csukva. ~6 mT be / 4,5 mT ki, kis neodímium mágnessel néhány mm–1 cm.
  SC-59 tok, kis hordozó NYÁK kell.

## Készlet értékelés (megtartandó)
WNS20S100C (100 V 2×10 A Schottky – polaritásvédelem, OR-olás) · SUM110P08-11L (P-FET, polaritásvédelem/felső
oldali kapcsoló, zener a gate-re) · IRF5305 (P-FET, TO-220, felső oldali kapcsoló) · BTA225B-600B (triac 230 V-ra,
optotriac: MOC3063 kapcsoláshoz, MOC3023 dimmeléshez) · BC546B, 2N3904, BC857B (+ BC847B pár kellene).
ATWINC1500 WiFi modul: a ModuNode-hoz nem kell.
