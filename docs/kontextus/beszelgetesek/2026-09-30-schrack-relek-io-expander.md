# Schrack relék, I/O expander – 2026-09-30

Forrás: claude.ai chat „50 Schrack SPDT relék”
(https://claude.ai/chat/ed5cf39a-0a1d-411a-927f-519411074fa5). Claude akkor a Windows-os
`Documents\szakdolgozat\ModuNode-Design-Reference.md` és `ModuNode_Prototipus_BOM.xlsx` alapján válaszolt.

## Háttér a Design Reference-ből
- A relé board 4 csatornás, **24 V-os tekercs** (§6), hogy ne kelljen harmadik tápsín. Meghajtó: **ULN2803A**,
  vezérlés I²C I/O expanderen át (PCF8574).
- A BOM-ban **Songle SRD-24VDC-SL-C** szerepel. A §8 2×2-es elrendezést és kb. 55–65 × 40–45 mm-es boardot becsül.
- A tervben **ADE7953** energiamérő is van (I²C, a 0x38–0x3F tartományban).

## Megállapítások
- Kb. 50 db **Schrack (TE) 24 V SPDT** relé van kézben, ez 12 boardra elég, plusz 2 tartalék. Jobb a Songle-nél:
  VDE, megerősített szigetelés.
- Ellenőrizendő: **pontos típuskód** (RT314024 / RT114024 / RP310024 → 12 vagy 16 A, érintkezőanyag, footprint),
  **DC tekercs-e** (a ULN-hez 24 VDC kell), bontott daraboknál a tekercsellenállás.
- Footprint: az RT1 keskenyebb és hosszabb, a 4 relé akár egy sorban is elfér. KiCad: Relay_THT könyvtár, Schrack RT1.
- Tekercsáram ~15–20 mA, ez a ULN2803A-nak nem gond.
- **PCF8574 probléma:** bekapcsoláskor minden kimenete HIGH (gyenge, ~100 µA), így boot alatt mind a 4 relé
  meghúz. → **TCA9554/PCA9554** javasolt: bemenetként indul (a ULN bemenetein lehúzó ellenállással biztosan OFF),
  push-pull kimenete van, címe 0x20–0x27, és az ESPHome támogatja.
- **Címütközés:** a PCF8574A/TCA9554A (0x38–0x3F) ütközne az ADE7953-mal → a nem-„A” változat kell.

## Nyitott
- A típuskód vagy egy fotó a reléről → a BOM relé lapjának és a Design Reference §6-nak a frissítése.
