# Ütemterv a NYÁK-rendelésig – 2026-10-14 → 2026-10-31

A D25 hármas felosztására épül: kapcsolási rajz → layout → átnézés + rendelés. Ami kész, azt pipáld ki; ha
csúszik valami, itt írd át a dátumot (a régi dátumot hagyd meg áthúzva: ~~10-16~~ 10-17).
Részletek: `MODULMAG-SPEC.md`, `VEZERLO-SPEC.md`, `NYAK-ELOKESZITES.md`, `SAMPLE-KERESEK.md`.

## 1. hét – döntések + kapcsolási rajz (10-14 Sze → 10-21 Sze)

| Nap | Balázs | Claude Code |
|---|---|---|
| Sze 10-14 | [x] **Sample-kérések elküldése** (TI elküldve 10-19, a többi gyártó még nem; TI először – ~5 munkanap a döntés) · [x] Schrack relé feliratának leolvasása (RTD14024, D62) | [x] ütemterv fájlba · [x] KiCad-projekt váz a repóban |
| Cs 10-15 | [x] **DIN-ház kiválasztása** → Gainta D4MG, NYÁK 86,5 × 68 mm (D73, 10-21) · [x] **D55 döntés** (nincs 24 V elleni védelem, PTC ki, TVS marad) · [ ] CubeMX-projekt mindhárom modulra (lábütközés, COMP2/DAC/TIM-break) | [x] a relé típuskódjából footprint + COM/NO/NC |
| P 10-16 – Szo 10-17 | [x] KiCad: **modulmag** hierarchikus lap (táp, STM32, ISO1042, busz-oldal) | [x] hiányzó szimbólumok/footprintek (ISO1042 DWV, P78E05, TCAN1044AV …) · [ ] a modulmag rajzának átnézése a spec alapján |
| V 10-18 | [x] KiCad: **vezérlő** (táp, C6, CAN, USB-C, W5500) | [ ] átnézés a VEZERLO-SPEC alapján |
| H 10-19 – K 10-20 | [x] KiCad: **LED-, relé-, bemeneti modul** (modulmag + a saját részük) | [ ] átnézés lapról lapra |
| Sze 10-21 → **Cs 10-22** (D71) | [x] ERC + javítások → **rajz lezárva** (10-22; D74–D80 után) | [x] teljes átnézés: `gen/ellenorzes.py` – 0 hiba (10-22) |

Esti, rövid feladatok ezen a héten:
- [~] ~~**W5500 + C6 breadboard-teszt**~~ elmarad (nincs kéznél a modul) → a rajz a WIZnet-referenciával összevetve, D72; (a kézben lévő modullal) **10-21 előtt** – a vezérlő SPI-lábkiosztásának
      (GPIO6/7/2/10/11/3) megerősítése, mielőtt a layout rögzül. Firmware: Claude Code.
- [ ] **A CCT szalag bekapcsolási felvillanása – 3 próba** (5 perc): (1) csak 24 V, C6 áram nélkül; (2) 24 V megy,
      C6 bedugás / RESET; (3) a szokásos bekapcsolás módja. Utána: CCT commit + `cp-03-cct-szalag`.

## 2. hét – layout (10-22 Cs → 10-28 Sze)

| Nap | Balázs | Claude Code |
|---|---|---|
| Cs 10-22 | [ ] **TI-válasz** → ami nem jön sample-ként, megrendelni (**LMR36015-re nincs tartalék**) · [x] rétegrend: 1 oz mindenhol, a nagyáramú sávok fedetlenek (D82) – impedancia: JLC-kalkulátor · [x] lapkörvonalak | [x] beszerzési lista (`SAMPLE-KERESEK.md` + `hardware/bom/*.csv`) |
| P 10-23 – Szo 10-24 | [ ] **modulmag** layout (újrahasznosítható blokk) · [ ] **LED-modul** (20 A-es sávok, sönt Kelvin-bekötéssel) | [ ] layout-ellenőrzőlista a két spec layout-fejezetéből |
| V 10-25 | [ ] **relé- és bemeneti modul** layout | |
| H 10-26 – K 10-27 | [ ] **vezérlő** layout (antenna keepout, Ethernet-párok, USB, VQFN buck) – 2 nap | |
| Sze 10-28 | [ ] DRC · [ ] 3D-ellenőrzés a DIN-házzal (P78E05 + elkó magassága) · [ ] szitanyomat (JP2 figyelmeztetés!) · [ ] fiducialok (stencil) | [ ] DRC-futtatás `kicad-cli`-vel |

## 3. hét – átnézés + rendelés (10-29 Cs → 10-31 Szo)

| Nap | Balázs | Claude Code |
|---|---|---|
| Cs 10-29 | [ ] JLC-árajánlat (4 réteg + stencil) | [ ] gerber-, fúrás- és BOM-ellenőrzés, footprint-irányok, BOM ↔ spec |
| **P 10-30** | [ ] javítások → **NYÁK + stencil megrendelése** · [ ] alkatrészek megrendelése (TME/Mouser/LCSC), hogy a NYÁK-kal együtt érkezzenek (≈ 11-10–15) | |
| Szo 10-31 | tartalék nap | |

## Kockázatok, tartalékterv
- **A layout a legszűkebb:** 4 lap ~6 nap alatt. Csúszás esetén 10-30-án a vezérlő + LED- + relémodul megy, a
  bemeneti modul (a többi nem függ tőle) egy héttel később, külön rendelésben.
- **TI-elutasítás:** 10-22-én azonnal rendelni. ISO1042 → breakout-tartalék (D36); LMR36015 → nincs tartalék.
- **Schrack relé típuskódja** nélkül a relémodul footprintje nem rajzolható → a hét első feladata.

## A rendelés után (november, a NYÁK-várakozás alatt)
- Matter-híd prototípus a DevKiten (HA dinamikus endpoint-teszt, D21)
- STM32 modul-firmware váz; CAN-protokoll + regisztertábla specifikáció (D31); bootloader (D20)
- Alkatrészek ≈ 11-10–15 → beültetés (reflow + stencil), élesztés modulonként
