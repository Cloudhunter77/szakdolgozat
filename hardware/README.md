# Hardver – KiCad 10 projektek

Specifikációk: `docs/kontextus/MODULMAG-SPEC.md`, `docs/kontextus/VEZERLO-SPEC.md`; ütemterv: `docs/kontextus/UTEMTERV.md`.

| Mappa | Mi |
|---|---|
| `lib/` | közös saját könyvtár: `modularis.kicad_sym`, `modularis.pretty/`, `3d/` |
| `modulmag/` | a modulmag **egyetlen** kapcsolási lapja; a három modul hierarchikus lapként használja (`../modulmag/modulmag.kicad_sch`), a saját projektje csak az önálló ellenőrzéshez kell |
| `vezerlo/` | ESP32-C6 vezérlő |
| `led-modul/`, `rele-modul/`, `bemeneti-modul/` | a modulok (modulmag + a saját részük) |

Laponként külön projekt = külön NYÁK, külön gerber. A modulmagot csak egy helyen kell javítani.

Ellenőrzés (Claude Code futtatja): `kicad-cli` (Flatpak: `flatpak run --command=kicad-cli org.kicad.KiCad`) –
ERC, netlista-export és összevetés a specifikációval, később DRC és gerber.
