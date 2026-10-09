# Soros logok – Matter over Thread, 2026-10-09

Az ESP32-C6 soros kimenete (`bash mt.sh log`), változtatás nélkül; csak a terminál-vezérlőkódok lettek kiszedve.
Az idő (`I (12345)`) a node indulásától számít, ms-ban. Jelszó, Thread hálózati kulcs nincs bennük.

| Fájl | Mit mutat | Kulcssorok |
|---|---|---|
| `2026-10-09-1-ha-attesztacios-hiba.log` | Google fabric sikeres, a HA 4× elutasítja a teszt tanúsítványt (még test-net DCL nélkül) | `AttestationRequest successful` → `ArmFailSafe (0s)` → `Commissioning failed (attempt N): 32` |
| `2026-10-09-2-sikeres-parositas.log` | Gyári reset utáni teljes párosítás: BLE → PASE → attesztáció → Thread → Google (fabric 1) + HA (fabric 2), utána fényerő parancsok | `Added new fabric at index: 0x1` / `0x2`, `Role detached -> child`, `Commissioning completed successfully` |
| `2026-10-09-3-szin-diagnozis.log` | Színváltogatás a HA-ból: a HA XY-ban küld (`MoveToColor`), a driver ezt nem kezeli | `Received command 0x00000007 ... cluster 0x00000300`, `Color X ... Color Y ...`, `Color mode not supported` |

Értelmezés: `docs/osszefoglalo-2026-10-09-matter-thread.md` (4–5. fejezet).
