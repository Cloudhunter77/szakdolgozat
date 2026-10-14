# A vezérlő kapcsolási specifikációja, repó-szinkron – 2026-10-13 (este) – 2026-10-14

Forrás: Cowork-munkamenet (claude.ai), a `2026-10-13-nyak-elokeszites-modulmag.md` folytatása; közben egy másik
chatben a modulmag tápja P78E05 lett (`2026-10-14-alkatreszkeszlet-p78e05.md`, D56, D57).
Döntések: **D58–D61** a `DONTESEK.md`-ben. Eredmény: `../VEZERLO-SPEC.md`.

## Balázs kérése és válaszai
- „A központi modult is szerkeszd meg, ha van kérdés tedd fel” → a vezérlő ugyanolyan részletes specifikációja,
  mint a modulmagé.
- Válaszok (D58): az **USB-C-ről is járjon**, de akkor busz nélkül · **2 átmenő XH** (a vezérlő a lánc végén vagy
  közepén) · **RGB LED + táp-LED** · bővítő tüskesor nincs, **csak debug**.
- 2026-10-14 (D59, D60): a V_BUS-t a kézben lévő **P78E05** adja (az LMR36006 helyett) · CAN transceiver:
  **TCAN1044AV** · a változások **közvetlenül a main-re** kerüljenek.

## A terv lényege (`VEZERLO-SPEC.md`)
- **Táp:** 24 V → F1 1 A → SS16 → két ág: (1) SS16 → LMR36015 (1 MHz, 6,8 µH) → 3,3 V a C6-nak és a W5500-nak;
  (2) 10 Ω (2512) → SMBJ28A + 47 µF elkó → P78E05 → 5 V a V_BUS-nak, a CAN transceivernek és az RGB LED-nek.
  Az **USB** egy 60 V-os Schottkyn át csak az (1) ágat táplálja.
- **V_BUS:** TPS2553, ILIM 61,9 kΩ → 382/425/476 mA; az EN egy osztóval a 24 V-os ágról jön → a V_BUS hardveresen
  csak 24 V mellett kapcsol be, a C6 újraindulása alatt is bekapcsolva marad; a GPIO20 egy BAT54-en át letilthatja.
  A modulon legrosszabb esetben ~4,7 V marad (ISO1042: ≥ 4,5 V).
- **ESP32-C6-WROOM-1-N16:** lábkiosztás – W5500 SPI GPIO6/7/2 (IO_MUX) + CS 10, RST 11, INT 3; CAN 18/19; VBUS_EN 20,
  FAULT 21; VIN_SENSE 0, VBUS_SENSE 1 (ADC1); RGB LED 8; BOOT 9; USB 12/13; UART0 16/17; tartalék 4, 5, 22, 23.
  A -1U a padok alapján ugyanarra a footprintre ültethető (Espressif KiCad-könyvtár).
- **W5500:** teljes lábkiosztás az adatlapból (RSVD 23 → GND, 38–42 nyitva, VBG nyitva, EXRES1 12,4 kΩ, TOCAP 4,7 µF,
  1V2O 10 nF); MDI-hálózat a WIZnet „use_mag” referenciájából (49,9 Ω-ok, 6,8/10/22 nF, 10 Ω) – a bekötést a
  referencia képén kell visszaigazolni; MagJack külön TCT/RCT lábbal (J1B1211CCD vagy HR911105A).
- **TCAN1044AVDRQ1** (±58 V, VCC 5 V, VIO 3,3 V, STB → GND); két 3 padas forrasztható jumperrel MCP2562FD, TCAN330 vagy
  SN65HVD230 is beültethető ugyanoda.
- **USB-C:** CC1/CC2 külön 5,1 kΩ, USBLC6-2SC6, 22 Ω-os soros ellenállások, 2,2 kΩ-os VBUS-levezető.
- **RGB LED:** WS2812B-V5 vagy a kézben lévő WS2812C-2020 az 5 V-ról, a kézben lévő 74HCT14-gyel szintillesztve
  (vagy 0 Ω-mal közvetlenül).

## A független ellenőrzés (subagent, adatlapokkal) eredménye – javítva
- A 40 V-os SS14 USB-dióda túlfeszültségnél (a 24 V-os oldal ~45 V-ig is felmehet) tönkremehetett volna, és
  zárlatosan 24 V-ot adott volna a laptop USB-portjára → **60 V-os** dióda.
- Az alapból bekapcsolt V_BUS (felhúzással) USB-ről táp-ingadozási hurkot okozott volna → **EN-osztó a 24 V-os ágról**.
- A kihúzott USB-C aljzat VBUS-a a dióda szivárgásától ~6 V-ra úszott volna → **2,2 kΩ-os levezető**.
- A WS2812B 3,3 V-ról specifikáción kívül van (min. 3,7 V) → **5 V-ról**, szintillesztővel.
- Apróbbak: TCAN1044AV csak -Q1 kóddal kapható SOIC-8-ban; a JP2 alapállása a 3,3 V-os típusokat tönkreteszi
  (szitanyomat-felirat); a debug-tüske 3,3 V-ja csak referencia; SPI-órajel kondenzátor-footprint; 6 dB-es
  ADC-csillapítás.
- Megerősítve: a C6, a W5500, a TPS2553, az LMR36015 és a TCAN1044AV lábai és értékei; az MCP2562FD lábról lábra azonos
  (±58 V); a WROOM-1U ugyanarra a footprintre megy.

## Repó-szinkron (D13)
- A 2026-10-13/14-i Projekt-dokumentumok a repó `docs/kontextus/` mappájába kerültek.
- **Számozási ütközés feloldva:** a repóban 2026-10-11-én D26-ként rögzített STM32F303RET6-döntés a Projekt
  számozásában D27 (tartalma összefésülve: PA11/PA12 indoka, saját CAN-bootloader, hardverréteg, a G431-es csereút);
  a D04 elvetése a D04 sorába került.
- Az `ATTEKINTES.md` a `CLAUDE.md` szabálya szerint ~150 sor alá rövidült; a részletek a két specifikációban.
- Ebből a munkamenetből a push nem engedélyezett (a repó nincs a munkamenet forrásai között) – lásd a válaszban.

## Források
- [ESP32-C6-WROOM-1/1U adatlap](https://documentation.espressif.com/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf) ·
  [ESP32-C6 adatlap](https://documentation.espressif.com/esp32-c6_datasheet_en.pdf) ·
  [Espressif hardvertervezési útmutató](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/schematic-checklist.html) ·
  [Espressif KiCad-könyvtár](https://github.com/espressif/kicad-libraries)
- [W5500 adatlap](https://docs.wiznet.io/img/products/w5500/W5500_ds_v110e.pdf) ·
  [WIZnet referencia-kapcsolás](https://docs.wiznet.io/Product/Chip/Ethernet/W5500/ref-schematic)
- TI: [LMR36015](https://www.ti.com/lit/ds/symlink/lmr36015.pdf) · [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf) ·
  [TCAN1044A-Q1](https://www.ti.com/lit/ds/symlink/tcan1044a-q1.pdf) · [TCAN330](https://www.ti.com/lit/ds/symlink/tcan330.pdf) ·
  [ESD2CAN24-Q1](https://www.ti.com/lit/ds/symlink/esd2can24-q1.pdf)
- [ST USBLC6-2](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) · [WS2812B-V5](https://cdn.eicom.ru/media/PDF/WS2812B-V5.pdf)
