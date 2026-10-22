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

## 2026-10-20 → 10-22 – Konzultáció utáni átdolgozás, NYÁK-előkészítés, L433-váltás, éjszakai ellenőrzés
- Csináltuk:
  - D71 (központi 5 V, közös föld, 12–26 V, HW-ID 16 sáv) mind az öt lapon;
  - D72 (W5500 a WIZnet-referencia szerint), D73 (Gainta D4MG, 86,5 × 68 mm), NYÁK-előkészítés (`gen/pcbgen.py`);
  - szakértői átnézés → D74–D77 (busz-GND R, CAN-fojtó, TVS-ek, bemenetvédelem, 230 V és antenna tiltott területei);
  - alkatrészkészlet-patch (claude.ai) → **D78–D80**: modul-MCU **STM32L433RCT3** (lábkiosztás: VIN_SENSE PB1, LED: TIM15/TIM16,
    I_SENSE PA3), modul-transceiver **SN65HVD230**, **N-FET a GND-ágban** mindhárom 24 V-os lapon, MCP9701A, zöld táp-LED a +5V-ról,
    2 oz a LED-/relémodulon, csavaros sorkapocs a LED 20 A-es útján, marad az AP2112K (a TC2117-nek tantál kellene);
  - éjszakai ellenőrzés: új `gen/ellenorzes.py` (ERC, láb ↔ pad, modulmag, CubeMX ↔ rajz ↔ L433-adatbázis, CubeMX fejsoros
    kódgenerálás, polaritásvédelem, NYÁK ↔ rajz, DRC, elavult szövegek), `gen/bom.sh` (darabjegyzék laponként);
    a CubeMX-projektek L4-es szintaxisra javítva (ADCx, DAC/COMP-csoport, TIM16 bekapcsolás, ADC-órajel);
  - komponenslista a konzulensnek (`docs/komponenslista.md`, a netlistákkal gépileg összevetve), PDF: `hardware/out/kapcsolasi-rajzok-2026-10-22.pdf`.
- Eredmény: 0 hiba az ellenőrzésen (csak szitanyomat-figyelmeztetés); a CubeMX mindhárom modulra minden perifériát generál.
  10-22 reggel, újabb teljes ellenőrzés: a NYÁK-footprintek UUID-útvonala egyik rajzi szimbólumra sem mutatott (a generátor
  minden futáskor új, véletlen UUID-t adott) → a szimbólum-UUID most a projekt + hivatkozási jel alapján stabil, a többi elemé
  laponként sorszámból képzett (két generálás bájtra azonos); a NYÁK-ok újragenerálva, mind a 581 footprint a szimbólumára mutat;
  az ellenőrző ezt is figyeli. Költségbecslés után (~140–220 e Ft/készlet): **D82 – 1 oz + fedetlen, utólag ónozott sávok** a 2 oz helyett.
- Tanultuk: az L4-es .ioc-ban az ADC-lábak megosztott jelként (ADCx) kellenek, és az ADC-órajel nélkül a CubeMX nem generál;
  a TPD4E05U06 letörése (6,4–8,7 V) az 5 V-tűrő láb határa körül van → D81 javaslat.
- Nyitott: huzalozás (Balázs, 10-26-ig); a D81 elvetve (marad a TPD4E05U06, 12/24 V-hoz osztó), a relékimenet 5,08 mm-es THT a készletből (D83);
  firmware-munkamenetnek: CCT_MAX_SUM 1.0-ra (D16 tisztázásáig), status_led.* commit; rendszer/kurzus artifact frissítése L433-ra.

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
