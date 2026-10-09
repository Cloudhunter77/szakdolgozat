# Checkpointok

Minden checkpoint egy **hardveren tesztelt**, működő állapot, annotált git taggel jelölve.
Visszaállás: `git switch -c <uj-ag> <tag>` · megtekintés: `git checkout <tag>` (vissza: `git switch main`)

| Tag | Dátum | Tartalom |
|---|---|---|
| `cp-01-esphome-demo` | 2026-10-09 | ESPHome vezérlő demó ESP32-C6-on |
| `cp-02-matter-thread-ha` | *tervezett* | Matter over Thread, párosítás Home Assistantba |

---

## cp-01-esphome-demo — 2026-10-09
**Mi működik**
- ESP32-C6 ESPHome firmware (`firmware/esphome-demo/modunode-c6.yaml`), webes kezelőfelület (`http://modunode-c6.local`)
- Relé 1 (GPIO18) kapcsolása weben és a BOOT gombbal
- Kézi / Automata üzemmód; Automata módban az ajtóérzékelő (GPIO19) vezérli a relét, csukás után állítható
  késleltetéssel kapcsol le
- RGB LED állapotjelzés, bootoláskor a relé mindig KI; a beállítások újraindítás után megmaradnak

**Hogyan lett tesztelve**
- Csupasz C6 boardon, Linux Mint alól USB-n flashelve; a vezérlés a webes felületről működött.

**Visszaállítás / újraépítés**
- `git checkout cp-01-esphome-demo` → `firmware/esphome-demo/README.md` szerint (`secrets.yaml` a
  `secrets.example.yaml`-ből)

---

## cp-02-matter-thread-ha — tervezett
**Feltétel:** a `firmware/matter-c6` firmware lefordul, a C6 Matter over Threaden párosodik a Home Assistantba,
és HA-ból kapcsolható a lámpa endpoint (a board RGB LED-je).
