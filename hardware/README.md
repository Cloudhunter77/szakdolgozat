# Hardver – KiCad 10 projektek

Specifikációk: `docs/kontextus/MODULMAG-SPEC.md`, `docs/kontextus/VEZERLO-SPEC.md`; ütemterv: `docs/kontextus/UTEMTERV.md`.

| Mappa | Mi |
|---|---|
| `lib/` | közös saját könyvtár: `modularis.kicad_sym`, `modularis.pretty/`, `3d/` |
| `modulmag/` | a modulmag **egyetlen** kapcsolási lapja; a három modul hierarchikus lapként használja (`../modulmag/modulmag.kicad_sch`), a saját projektje csak az önálló ellenőrzéshez kell |
| `vezerlo/` | ESP32-C6 vezérlő |
| `led-modul/`, `rele-modul/`, `bemeneti-modul/` | a modulok (modulmag + a saját részük) |
| `gen/` | a vázlatok generátora: `gen/build.sh <lap>` → `<lap>.py` → `.kicad_sch` + ERC, netlista, PDF az `out/`-ba. **Felülírja a kézi elrendezést** – elrendezés után már csak kézzel módosítsd a lapot |

Laponként külön projekt = külön NYÁK, külön gerber. A modulmagot csak egy helyen kell javítani.

Ellenőrzés (Claude Code futtatja): `kicad-cli` (Flatpak: `flatpak run --command=kicad-cli org.kicad.KiCad`) –
ERC, netlista-export és összevetés a specifikációval, később DRC és gerber.

## Munkafolyamat (D67)

- **Forrás:** amíg Balázs egy lapot nem szerkeszt kézzel, a `gen/<lap>.py` a forrás. Amint kézzel átrendez rajta
  valamit, onnantól a `.kicad_sch` – arra a lapra a generátort **nem futtatjuk újra** (a mozgatások elvesznének).
  A kézzel átvett lapokat itt jelöljük: _(még egyik sem)_.
- **Egyszerre csak egyikünk szerkeszt:** Balázs ment → Claude módosít (fájlban vagy KiCad MCP-vel) → Balázs a
  KiCad-ben újratölti a lapot (File → Revert).
- **Minden módosítás után:**
  - `gen/build.sh <lap>` (csak generátoros lapnál) – ERC-t is futtat, `Found 0 violations` kell
    (a `modulmag` önállóan ~55 jelzést ad a lógó hierarchikus lábak miatt – ez rendben van, a modulok ERC-je a mérvadó)
  - netlista-összevetés: `kicad-cli sch export netlist -o out/<lap>.net <lap>/<lap>.kicad_sch`, majd
    `python3 -I gen/netcmp.py out/<lap>.before.net out/<lap>.net` – a bekötés változatlan, ha 0 / 0 eltérés
    (relé és LED: 4 várt eltérés a D6/JP2 buszos táp opció miatt). Az `out/` gitignore-ban van, a `.before.net`
    csak helyben létezik; szándékos bekötés-változás után újra kell menteni.
  - vizuális ellenőrzés: KiCad MCP `sch_visual_qa` – a „symbol_overlap” többnyire formai (tápszimbólum a láb végén,
    szomszédos alkatrész, többegységes U9), ezért PDF → PNG kivágáson is megnézni.
- **KiCad MCP:** `kicad-mcp-pro` (uvx, Python 3.13), helyi scope, munkaterület = `hardware/`, **írható mód**
  (`KICAD_MCP_OPERATING_MODE=write`). Minden projektmappában `output/` munkamappát hoz létre (gitignore-ban).

## STM32CubeMX-projektek (`cubemx/`)
`python3 gen/cubemx.py` → `cubemx/<modul>/<modul>.ioc` a MODULMAG-SPEC 7. fejezetének lábkiosztásából (a jel- és
üzemmódnevek a CubeMX 6.18 adatbázisából). MCU: **STM32L433RCT3** (D78). Indítás: `flatpak run com.st.STM32CubeMX` →
File → Load Project. A pinout nézet a lábhozzárendelést ellenőrzi; a belső kapcsolatokat (COMP2 → TIM1/TIM15/TIM16 BKIN,
DAC1_OUT1 → COMP2 INM, ADC1_IN8 + COMP2_INP a PA3-on) a CubeMX-ben kézzel kell beállítani és megnézni.

## Teljes ellenőrzés (`gen/ellenorzes.py`, 2026-10-22)
`python3 gen/ellenorzes.py` (a `hardware/` mappából) – minden lapot újragenerál és ellenőriz:
1. ERC (elfogadott: a modulmag önálló hierarchikus jelzései, a relén a 4 lib-jelzés);
2. minden bekötött szimbólumláb létezik-e a footprinten (láb ↔ pad);
3. a modulmag bekötése mindhárom modulban (L433 táplábak, SN65HVD230, AP2112K, táp-LED, BOOT0, busz-GND);
4. a CubeMX-projekt címkéi ↔ a rajz hálózatai ↔ az L433-adatbázis (rendelhető-e a jel a lábhoz); 4b. a CubeMX
   fejsorból betölti az .ioc-kat és kódot generál (`out/cubemx-test/`) – minden periféria inicializálódik-e;
5. a GND-ági polaritásvédő FET-ek (D78) bekötése;
6. NYÁK ↔ rajz (alkatrészek, padok hálózatai, footprintek, szimbólum-kapcsolat), 1 oz-os rétegrend (D82), tiltott területek, DRC;
7. elavult kifejezések a generátorokban és a dokumentációban (csak figyelmeztetés).
Kapcsolók: `--no-build` (a meglévő netlistákból), `--no-cubemx`. „HIBA” = javítandó; a szitanyomat-jelzések a
layoutnál rendeződnek (figyelmeztetés). Kilépési kód 1, ha van hiba.

**UUID-k (10-22):** a generátor determinisztikus – a szimbólumok UUID-je a projekt + hivatkozási jel alapján képződik, így
újragenerálás után is egyezik a NYÁK footprintjeinek útvonalával („Update PCB from Schematic” működik); a többi elem UUID-je
laponként sorszámból képződik (két futás bájtra azonos fájlt ad).

## Darabjegyzék (`gen/bom.sh`)
`bash gen/bom.sh` → `bom/<lap>.csv` – laponként, értékenként és footprintenként csoportosítva, a DNP-k nélkül
(a „Megjegyzés” mezővel). A kézben lévő és a megveendő tételek: `docs/kontextus/SAMPLE-KERESEK.md`.

## NYÁK-előkészítés (2026-10-21, D73)
`gen/pcbgen.py` a netlistából (`out/<lap>.net`) elkészíti a `<lap>/<lap>.kicad_pcb`-t: 4 réteg, körvonal (86,5 × 68 mm;
a bemeneti modul 86,5 × 103 mm), DIN-zónák a Dwgs.User rétegen (felső/alsó váll, előlapi ablak), a footprintek a
hálózatokkal és a kapcsolási rajzhoz kötve (az „Update PCB from Schematic” működik), kezdő elhelyezés: a csatlakozók
a ház szerinti élen, a többi a hozzá kötött IC köré. Huzalozás nincs – azt kézzel.

    flatpak run --command=python3 org.kicad.KiCad gen/pcbgen.py <lap> [--force]   # board generálása
    gen/pcbshow.sh <lap> kep.png                                                  # kép ellenőrzéshez

**A D67 a NYÁK-ra is érvényes:** amint egy `.kicad_pcb`-t kézzel szerkesztettél, az a forrás; a szkript csak
`--force`-szal írja felül. Kapcsolási rajz változása után a KiCad-ben: *Tools → Update PCB from Schematic*.
