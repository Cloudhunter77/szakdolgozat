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
