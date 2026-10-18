# ModuNode – szakdolgozat (moduláris okosotthon platform)

Balázs szakdolgozata: moduláris okosotthon node-ok ESP32-C6-on, végleges iránya **Matter (over Thread) +
Home Assistant**. Balázs magyarul kommunikál, Linux Mint alatt dolgozik, Linuxban kezdő – a parancsokat röviden
magyarázd el.

## Alapszabály: mit szabad kérdés nélkül
**Kérdés nélkül szabad:** olvasni, keresni, buildelni, logot nézni, és a repón belül fájlt létrehozni /
módosítani (a git a visszavonás gomb).
**Előbb kérdezz, várd meg a jóváhagyást:** git commit / tag / push, fájl törlése vagy mozgatása, csomag- vagy
toolchain-telepítés, flashelés, flash törlés.
`sudo`-t soha ne futtass – írd ki a pontos parancsot, és Balázs futtatja a saját termináljában.

## Párhuzamos munkamenetek
Gyakran több Claude munkamenet fut egyszerre ezen a repón. Mindegyik a saját mappájában dolgozik
(`firmware/`, `hardware/`, `docs/`); commit előtt `git status` – más munkamenet módosításaihoz ne nyúlj.

## Repó szerkezet
```
docs/                    tervek, jegyzetek, szakdolgozat anyagok
firmware/esphome-demo/   ESPHome vezérlő demó (C6) – saját CLAUDE.md
firmware/matter-c6/      ESP-Matter, Thread (C6) – saját CLAUDE.md
CHECKPOINTS.md           checkpoint napló
```
Ha egy `firmware/*` alprojektben dolgozol, előbb olvasd el annak a `CLAUDE.md`-jét.

## Git munkamenet
- Kis, egy témájú commitok, magyar üzenettel (pl. „Matter: ajtóérzékelő endpoint hozzáadása”).
- Commit előtt mutasd a `git status`-t és a diff lényegét; push csak jóváhagyás után.
- **Titok soha nem kerülhet a repóba** (`secrets.yaml`, WiFi jelszó, API kulcs). Új titok → `secrets.yaml`,
  a sablonja → `secrets.example.yaml`. Kétség esetén `git check-ignore -v <fájl>`.
- Build kimenet (`build/`, `.esphome/`, `managed_components/`, `sdkconfig`) nem kerül fel.
- Az ESP-IDF `dependencies.lock` **felkerül** – ez rögzíti a pontos komponens verziókat (reprodukálható build).

## Checkpointok
Checkpoint = **hardveren tesztelt**, működő állapot. Közben sima commitok mennek, tag nélkül.
1. Balázs megerősíti, hogy a hardveren működik.
2. Új bejegyzés a `CHECKPOINTS.md`-ben (dátum, mi működik, hogyan lett tesztelve, hogyan állítható vissza) –
   ez a checkpoint commit része.
3. Annotált tag: `git tag -a cp-NN-rovid-nev -m "<egy mondat>"` (NN kétjegyű sorszám, ékezet nélkül).
4. `git push origin main --follow-tags`

Visszaállás egy checkpointra: `git switch -c probalkozas cp-01-esphome-demo` (új ágon), vagy csak megnézni:
`git checkout cp-01-esphome-demo` (detached HEAD – vissza: `git switch main`).

## Projekt kontextus
@docs/kontextus/ATTEKINTES.md

További háttér, csak ha a téma előkerül: `docs/kontextus/DONTESEK.md` (döntésnapló), `docs/kontextus/beszelgetesek/` (claude.ai chat-jegyzetek), `docs/kontextus/NAPLO.md` (munkanapló).

### A kontextus karbantartása
- Érdemi munkamenet végén Balázs `/wrap`-et futtat: ez frissíti a `NAPLO.md`-t, az `ATTEKINTES.md`-t és a
  `DONTESEK.md`-t, majd commitot ajánl. Ha elfelejti, emlékeztesd.
- Új döntés → új sor a `DONTESEK.md`-ben; ha az állapot vagy egy nyitott kérdés változik → `ATTEKINTES.md`.
- A `beszelgetesek/` jegyzeteit Claude a claude.ai oldalon írja; te ezeket csak commitolod, nem írod át.
- Az `ATTEKINTES.md` maradjon rövid (kb. 150 sor alatt), mert minden munkamenetben betöltődik.
