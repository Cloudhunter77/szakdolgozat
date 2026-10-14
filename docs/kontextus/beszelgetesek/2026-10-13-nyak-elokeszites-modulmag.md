# NYÁK-előkészítés, modulok pontosítása, modulmag-specifikáció – 2026-10-13 (délután–este)

Forrás: Cowork-munkamenet (claude.ai), a `2026-10-13-can-izolacio-stm32f303.md` folytatása.
Döntések: D37–D55 a `DONTESEK.md`-ben. Eredmények: `../NYAK-ELOKESZITES.md`, `../MODULMAG-SPEC.md`,
`../V2-OTLETEK.md`, `../SAMPLE-KERESEK.md`.

> **Felülírja** az előző jegyzet „A lezárás változatlan (120 Ω a vezérlőn + lezáródugó; osztott lezárás)” mondatát:
> a lezárás **sima 120 Ω jumperrel** minden lapon, csak a lánc két végén bedugva (D49, D52).

## v2-re halasztva (D37, `V2-OTLETEK.md`)
Relémodul fogyasztásmérése, PoE, 48 V-os változat, olcsóbb MCU, átjáró-modulok, MQTT/Zigbee, csatornánkénti
LED-árammérés. A relémodulon a mérésnek való helyfoglalás: javaslat, nincs megerősítve.

## Csatlakozók: XH a buszra, PH az érzékelőkre (D38, D51)
- Busz: **JST-XH 4 tű** (2,5 mm, 3 A). Érzékelők: **3 tűs JST-PH javasolt** (2,0 mm, keskenyebb, és nem dugható a
  busz XH-jába → érzékelő nem kerülhet a buszra). Balázs: „xh mehet”.
- Minden érzékelő **külön** 3 tűs csatlakozón (Balázs: ne legyen 10 tűs ott, ahol 1 dolgot kell figyelni).

## Modulok
- **LED-modul: 6 csatorna** (D43) – „használjuk ki az STM lábait”: 2 × RGB, 3 × CCT vagy 6 × egyszínű.
  - Balázs ötlete „3 GND + 6 csatorna” volt; mivel a kapcsolás low-side, a szalagok közös vezetéke a **+24 V** →
    kimenet: 3 × [+24 V, CHa, CHb]. Egyszínű szalagnál kettő egy +24 V-on (iker érvéghüvely).
  - 20 A össz-áram a 3 eres (230 V-os) kábelen: barna +24 V, kék GND, a zöld-sárga nem használható; „24 V DC” jelölés.
  - **Mérés (D47):** bemeneti és biztosíték utáni 24 V, össz-áram söntön + INA → ADC + komparátor → hardveres
    lekapcsolás. Balázs: csatornánkénti áram nem kell, elég az össz-áram és a kitöltés-alapú becslés; az
    induláskori önteszt (halvány villanás) maradhat.
- **Általános bemeneti modul: 16 bemenet** (D44, D48) – Balázs: 16-nál több sehol nem kell, ha mégis, még egy modul
  kerül a láncra; bővítő modul a modulhoz nem lesz. A komódhoz 6 fiók → 6 AH1911.
- **Vezérlő: Ethernet a NYÁK-on** (D45) – W5500 + MagJack, opcionálisan beültetve; Balázs nem akar külön modult.
- Buck a 24 V-ról: minden modulon (LMR36006 → 3,3 V); a vezérlőn két buck, 3,3 V és 5,2 V (D46).

## NYÁK és mechanika (D42, D49, D50)
- 4 rétegű, minél kisebb lap (ha nem sokkal drágább – JLC-árat ellenőrizni).
- **DIN 43880-as ház-forma** (javaslat): a NYÁK a ház alján; felső váll: 24 V + busz BE/KI + lezáró jumper; alsó
  váll: terepi csatlakozók; előlap: állapot-LED-ek fényvezetővel. Becslés: vezérlő, LED-, relémodul 4 M
  (~66 × 85 mm NYÁK), bemeneti modul 6 M (~100 × 85 mm). Gyári DIN-ház belső méretére tervezni, a 3D-nyomtatott ház
  ugyanerre a formára.

## Modulmag-specifikáció (D52–D55) → `../MODULMAG-SPEC.md`
Balázs kérése: „ma este elkezdem rajzolni KiCad-ben” – ezért minden alkatrész értékkel, minden bekötés, és egy
lábkiosztás, ami mindhárom modult egyszerre lefedi. Az ST hivatalos lábadataiból (STM32_open_pin_data) és a TI
adatlapokból készült, majd egy független átnézés után javítva.

Fő pontok és a közben talált hibák:
- **Táp:** F1 0,5 A → SS16 → SMBJ28A → LMR36006**B**RNXR (1 MHz; a 2,1 MHz-es „C” 24 V → 3,3 V-ra a min.
  bekapcsolási idő miatt specifikáción kívül) → 3,31 V (100 k / 43,2 k). PG → GND, EN → VIN.
- **LED-modul logikai tápja a 20 A-es főbiztosíték ELŐTT** ágazik le (D54) – az első változatban utána volt, így a
  kiégett biztosítékot a modul nem tudta volna jelezni.
- **Túláram-küszöb a DAC1-ről** (D53): az első változat fix VREFINT-küszöbe (~24 A) egy 15 A-es táppal soha nem
  oldott volna ki. Az INA181A3 (×100) helyett **INA181A2 (×50)**, hogy 20 A felett is legyen mérési tartomány.
  COMP2 → TIM1 + TIM8 BKIN2.
- **Lezárás: sima 120 Ω** (D52) – az osztott lezárást egyetlen jumperrel nem lehet tisztán kikapcsolni.
- **Lábkiosztás (D54):** CAN PA11/PA12, debug-UART USART1 PC4/PC5 (így a PA9/PA10 a TIM1-é), SWD, HSE, HW-ID PC0,
  VIN_SENSE PC1; LED: TIM1 PA8–PA10 + TIM8 PC6–PC8, PA7 I_SENSE, PA4 DAC1, PB12 DRV_EN; relé PB12–PB15;
  bemeneti modul 16 különböző EXTI-vonalon, I²C1 PB8/PB9. CubeMX-ben ellenőrizni.
- **Átnézés utáni javítások:** V_BUS-PTC 0,2 A → 0,5 A, ≤ 0,5 Ω; UCC27524 EN-lehúzás 10 k → 4,7 k; VDDA-ferrit kis
  DCR-ű vagy 0 Ω; opcionális bemeneti elkó; a vezérlő V_BUS-a 5,2 V.
- **Nyitott (D55):** az ISO1042 VCC2 abszolút max. 6 V, a TVS + PTC egy félredugott 24 V ellen nem véd biztosan →
  Balázs dönt: TVS + PTC marad (v1) vagy TPS2660 minden modulon.

## Források
- [ST STM32_open_pin_data – STM32F303R(D-E)Tx](https://github.com/STMicroelectronics/STM32_open_pin_data)
- [TI LMR36006 adatlap](https://www.ti.com/lit/ds/symlink/lmr36006.pdf) ·
  [TI ISO1042](https://www.ti.com/lit/ds/symlink/iso1042.pdf) ·
  [TI INA181](https://www.ti.com/lit/ds/symlink/ina181.pdf) ·
  [TI UCC27524](https://www.ti.com/lit/ds/symlink/ucc27524.pdf) ·
  [TI TLV755P](https://www.ti.com/lit/ds/symlink/tlv755p.pdf) ·
  [TI ESD2CAN24-Q1](https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf)
- ST AN4206 (STM32F3 hardver – első lépések)
