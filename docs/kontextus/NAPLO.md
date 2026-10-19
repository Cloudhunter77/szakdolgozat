# Munkanapló (helyi Claude Code)

Minden érdemi munkamenet végén egy bejegyzés, **a legújabb felül**. Rövid legyen: mit csináltunk, mi lett
az eredmény, mi maradt nyitva. Ha közben döntés született, az a `DONTESEK.md`-be kerül; ha változott az
állapot vagy egy nyitott kérdés, frissítsd az `ATTEKINTES.md`-t is. A naplózás is módosítás → előtte kérdezz.

Sablon:
```
## ÉÉÉÉ-HH-NN – rövid cím
- Csináltuk: …
- Eredmény: … (commit/tag: …)
- Nyitott: …
```

---

## 2026-10-14 → 10-19 – Kapcsolási rajzok KiCad-ben (mind az öt lap), TI-kérés
- Csináltuk: grill-döntések D62–D67; Python-generátor (`hardware/gen/`) → relé-, LED-, bemeneti modul, vezérlő,
  modulmag hierarchikus lapként; mind az öt lap vezetékes, blokkos elrendezése; netlista-összevető (`gen/netcmp.py`,
  alap: `hardware/out/*.before.net`); KiCad MCP Pro telepítve (uvx, helyi scope), vizuális QA alapján olvashatósági
  javítások; TI sample-kérés + TI-rendelés leadva (10-19, Chrome-ban kitöltve); konzultációs összefoglaló (artifact).
- Eredmény: ERC 0 mindenhol (relé: 4 lib_symbol_mismatch elfogadva), a bekötés az átrendezés előttivel azonos
  (commitok: 59316b7, 5345f48).
- Tanultuk: az MCP `sch_visual_qa` „symbol_overlap” jelzései többnyire formaiak (tápszimbólum a láb végén, szomszéd
  alkatrész, többegységes U9) – képen (PDF → PNG) érdemes ellenőrizni; a generátor felülírja a kézi elrendezést (→ D67).
- Nyitott: lapról lapra átnézés a spec szerint (10-21 lezárás); DIN-ház; CubeMX; W5500 + C6 breadboard-teszt;
  többi sample-kérés (10-22); a KiCad MCP írható módja csak Claude Code újraindítás után él.

## 2026-10-11 – Bemutató után: architektúra behúzva, STM32 azonosítva
- Csináltuk: a claude.ai-ból jött bundle (D15–D25, node/modul architektúra, 2 chat-jegyzet) behúzva és pusholva;
  a lejárt GitHub token megújítva (`gh auth login`); a modul MCU azonosítva.
- Eredmény: modul MCU = STM32F303RET6 (8 db, van bxCAN) → a CAN-busz marad (D19, D26); D04 elvetve;
  a `matter-c6/CLAUDE.md` következő fázisa a Matter-híd (D21).
- Nyitott: sample-kérések; modulmag kapcsolási rajz (EDA program még nincs eldöntve); lábkiosztás ellenőrzése az
  adatlapból (F303 ↔ G431, AN5093); a HA dinamikus endpoint teszt a DevKiten.

## 2026-10-09 – Matter over Thread: első build és párosítás HA-ba
- Csináltuk: projekt kontextus commit; ESP-IDF v5.5.5 setup; Matter build (hiányzó `common_macros.h` pótolva);
  erase + flash; párosítás a HA appból (Android).
- Eredmény: a C6 Thread routerként a hálón, két fabricben: Google (fabric 1) + HA (fabric 2); a board LED-je
  HA-ból vezérelhető (ki/be, fényerő); BOOT gomb → azonnal frissül a HA-ban. Szín csak részben (piros, kék):
  a HA XY-ban küldi (`MoveToColor`), a driver ezt nem kezeli. (tag: `cp-02-matter-thread-ha`)
- Akadályok: a Developer Console integráció nem volt mentve; a HA Matter Server elutasította a teszt DAC-ot →
  „Enable test-net DCL usage”; a `mt.sh log` porton nyitáskor reseteli a C6-ot.
- Nyitott: `serial_log.py` reset-javítás; LED driver XY színmód; ModuNode endpointok (relé GPIO18, ajtó GPIO19).

## 2026-10-09 – Repó beállítás
- Csináltuk: a repó klónozása, `firmware/esphome-demo` és `firmware/matter-c6` beköltöztetése, `cp-01-esphome-demo` tag.
- Eredmény: commitok (repó váz, ESPHome demó, Matter projekt), `cp-01-esphome-demo` tag, push a GitHubra kész.
- Nyitott: Matter build + párosítás (`cp-02`)
