# v2 – későbbre halasztott ötletek

Ami nem kerül a védésre készülő prototípusba (v1, NYÁK-rendelés ≈ 2026-10-31), de a dolgozatban
„továbbfejlesztési lehetőségként” megemlíthető. Új tétel a lista aljára, forrással.

| Ötlet | Mi kell hozzá | Miért nem most | Forrás |
|---|---|---|---|
| **Fogyasztásmérés a relémodulon** | ADE7953 energiamérő IC (valós, teljesítménytényezővel korrigált teljesítmény) vagy egyszerűbben SCT-013-030 áramváltó + feszültségmérés az STM32 ADC-jére; 230 V-os mérőoldal leválasztással | Sok tervezés és kockázat a 230 V-os oldalon; a határidőbe nem fér | D37 (2026-10-13) |
| **PoE a vezérlőn** | PoE-fogadó (802.3af) + izolált DC-DC a már meglévő W5500 + MagJack mellé (a MagJacknek PoE-képesnek kell lennie) | Túl sok új részegység; a v1 vezérlő 24 V-ról jár. A PoE eleve galvanikusan leválasztott, jól illik az izolált buszhoz | D37 (2026-10-13) |
| **48 V-os, pl. kerti változat** | 48 V-hoz méretezett TVS, 80–100 V-os buck és FET, 48 V-os relé, nagyobb feszültségű kondenzátorok; a hosszú kábel miatt a V_BUS táplálását újragondolni; kisebb CAN-bitráta | Nem fix, nagyobb távolságokhoz kell; a busz oldal (ISO1042, ±70 V) már kész | D34 |
| **Olcsóbb modul-MCU** | pl. STM32G0/G4 (FDCAN) – új layout (más lábkiosztás), a CAN-meghajtó absztrakciós réteg mögött | Az F303RET6-ból 8 db van, a prototípushoz elég | D27 |
| **Átjáró-modulok** | pl. RS-485/Modbus (meglévő fogyasztásmérők), DALI – új modultípusként, ugyanazon a CAN-buszon | A v1-ben csak LED, relé, bemeneti modul | D32 |
| **További node-protokollok** | MQTT a Wi-Fi/Ethernetes node-okra; Zigbee firmware-változat (a C6 egyszerre csak Thread VAGY Zigbee) | A v1 Matter over Thread | D32 |
| **Csatornánkénti árammérés a LED-modulon** (alacsony prioritás) | 6 sönt + erősítő (az F303 4 belső műveleti erősítője PGA-módban + 2 külső), Kelvin-bekötés csatornánként | Balázs szerint nem fontos; a v1-ben az össz-áram + induláskori önteszt + kitöltés-alapú becslés elég | D47 (2026-10-13) |
| **Második modul-lánc a vezérlőn** | a C6 második TWAI vezérlője (a NYÁK-on a GPIO22/23 tesztpadként fenntartva) + egy második transceiver, lezárás és V_BUS-kapcsoló | A v1-ben egy lánc elég (2 átmenő XH, D58) | D58, `VEZERLO-SPEC.md` 3.2 (2026-10-14) |

## Megjegyzések
- A fogyasztásméréshez szükséges SCT-013-030 az AliExpress-rendelésből kimaradt – a v1-hez így nem kell pótolni.
- Az ADE7953 sample-t (ADI) most nem kell kérni.
- Javaslat: a v1 relémodul NYÁK-ján ne foglaljunk helyet a mérésnek, a v2 legyen új relémodul-revízió (nincs
  megerősítve).
- 16-nál több bemenethez nem bővítő, hanem még egy bemeneti modul kerül a láncra (D48) – ez nem v2-es tétel,
  a rendszer így működik.
