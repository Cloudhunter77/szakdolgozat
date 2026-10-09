# ModuNode C6 – vezérlő demó (szakdolgozat)

ESPHome firmware egy ESP32-C6 boardra. Cél: **bemutatható vezérlés még ma**, külső alkatrész nélkül is.
A felhasználó (Balázs) magyarul kommunikál, Linux Mint (Cinnamon) alatt dolgozik, Linuxban még kezdő – a
parancsokat röviden magyarázd el, mielőtt futtatod.

A repó gyökerében lévő `CLAUDE.md` (git munkamenet, checkpointok) erre a mappára is érvényes.

## Fájlok
- `modunode-c6.yaml` – a firmware konfig (ESPHome 2026.9-cel validálva, `esphome config` OK)
- `secrets.yaml` – WiFi + kulcsok. **Soha ne commitold, ne írd ki a tartalmát a chatbe.** (gitignore-olva)
- `secrets.example.yaml` – a secrets.yaml sablonja, ez van a repóban
- `setup.sh` – ESPHome telepítése venv-be (`~/.venvs/esphome`), környezet-ellenőrzés
- `README.md` – bemutató forgatókönyv embernek

## Parancsok
```bash
bash setup.sh                                   # egyszer: ESPHome telepítés + ellenőrzés
E=~/.venvs/esphome/bin/esphome
$E config  modunode-c6.yaml                  # validálás
$E run     modunode-c6.yaml --device /dev/ttyACM0   # fordít + USB-n flashel + logot mutat
$E run     modunode-c6.yaml --device modunode-c6.local  # később: OTA WiFi-n
$E logs    modunode-c6.yaml                  # csak log
$E dashboard .                               # opcionális webes felület: http://localhost:6052
```
Az **első fordítás 5–15 perc** (letölti az ESP-IDF toolchaint), ez normális – szólj a felhasználónak, ne szakítsd meg.
A `run` a végén logot streamel és nem lép ki magától: futtasd úgy, hogy le tudd állítani (pl. `timeout 60`),
vagy flashelés után külön `logs`-szal nézd.

## sudo szabály
`sudo`-t igénylő parancsot **ne futtass** (jelszót kérne, elakadsz). Írd ki a pontos parancsot, és kérd meg
Balázst, hogy a saját termináljában futtassa. Tipikusan:
- `sudo apt install -y python3-venv python3-pip` – ha a venv létrehozása `ensurepip` hibával elhasal
- `sudo usermod -aG dialout $USER` – soros port jogosultság; utána **ki- és bejelentkezés** (vagy újraindítás) kell.
  Gyors, ideiglenes alternatíva: `sudo chmod a+rw /dev/ttyACM0`
- `sudo apt remove brltty` – ha CH34x USB-UART-os boardnál a `/dev/ttyUSB0` megjelenik majd azonnal eltűnik

## Board és lábak
Feltételezett board: **ESP32-C6-DevKitC-1** (a „C6 Super Mini” és a Waveshare C6-Zero is ugyanígy működik).
Ellenőrzés: `lsusb` → `303a:1001` = natív USB-Serial-JTAG (`/dev/ttyACM*`), `1a86:...` = CH34x UART híd
(`/dev/ttyUSB*` vagy `/dev/ttyACM*`). A DevKitC-1-en két USB-C van, bármelyik jó.

| Funkció | Láb | Megjegyzés |
|---|---|---|
| RGB állapot LED (WS2812) | GPIO8 | strapping láb, LED-re rendben |
| BOOT gomb | GPIO9 | strapping láb, bemenetként rendben |
| Relé 1 kimenet | GPIO18 | relé-modul IN vagy LED + 330 Ω a GND felé |
| Ajtó bemenet | GPIO19 | belső felhúzás; GND-re húzva = csukva |

Ha a board más (pl. XIAO ESP32-C6: nincs RGB LED, sima LED a GPIO15-ön), a `substitutions:` blokkban kell
átírni, a többi konfighoz nem kell nyúlni. **Ne használd** relé/bemenet célra: GPIO4, 5, 8, 9, 15 (strapping),
GPIO12–13 (USB), GPIO16–17 (UART0 konzol).

Ajtóérzékelő élesben: **AH1911** Hall-kapcsoló (Diodes Inc.) – 1,6–5,5 V, push-pull kimenet, mágnes jelenlétében
LOW → a konfig logikájával ez „csukva”. Bekötés: VDD → 3V3, GND → GND, OUT → GPIO19 (lábkiosztás az adatlapból).
A 24 V-os Schrack relék közvetlenül nem köthetők GPIO-ra – ULN2803A meghajtó + 24 V táp kell; a mai demóhoz
elég egy LED vagy egy 3,3 V-tal vezérelhető relé-modul.

## Vezérlési logika (a yaml-ban)
- `select uzemmod`: Kézi / Automata (NVS-ben megmarad)
- Automata: ajtó nyit → relé BE azonnal; ajtó csuk → `number kesleltetes` mp múlva relé KI (`script kesleltetett_kikapcs`)
- Automata módba lépéskor a relé szinkronizál az ajtó állapotához (`script automata_szinkron`)
- BOOT gomb: rövid = relé váltás, ≥1,5 s = üzemmód váltás
- RGB LED (`script led_frissites`): zöld = relé BE, kék = Automata vár, sötét = Kézi + relé KI
- Relé `restore_mode: ALWAYS_OFF`: bootoláskor mindig KI (biztonságos alapállapot – szakdolgozati érv)

## Hibaelhárítás
- Nem csatlakozik flasheléskor → BOOT nyomva tart, RESET megnyom, BOOT elenged (download mód), újra `run`
- `Permission denied: /dev/ttyACM0` → dialout csoport (lásd sudo szabály)
- Nem jön fel WiFi-n → csak 2,4 GHz-es hálózat jó; ha nem éri el, „ModuNode-C6” hotspotot nyit
  (jelszó a secrets.yaml-ban), arra csatlakozva a 192.168.4.1 címen állítható be a WiFi
- `modunode-c6.local` nem oldódik fel → az IP címet a logból (`$E logs`) vagy a routerből vedd
- Az ESPHome fordítási hibáinál először a `esphome config` kimenetét nézd, és a hivatalos doksit (esphome.io)
