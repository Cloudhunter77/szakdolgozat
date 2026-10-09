# ModuNode C6 – vezérlő demó

ESP32-C6 + ESPHome: helyi (felhő és Home Assistant nélküli) vezérlési logika, webes kezelőfelülettel.

## Indítás (első alkalom, ~20 perc)
1. `cp secrets.example.yaml secrets.yaml`, majd töltsd ki: WiFi név + jelszó (2,4 GHz-es hálózat), kulcsok
2. Terminálban ebben a mappában: `bash setup.sh` – amit sárgával kér (sudo), azt futtasd le
3. C6 bedugva: `~/.venvs/esphome/bin/esphome run modunode-c6.yaml --device /dev/ttyACM0`
4. Böngészőben: **http://modunode-c6.local** (vagy a logban kiírt IP)

Vagy egyszerűen kérd meg a Claude Code-ot ebben a mappában: *„flasheld fel a C6-ra”* – a `CLAUDE.md` alapján tudja a lépéseket.

## Bemutató forgatókönyv (~3 perc)
| # | Mit csinálsz | Mit lát a közönség |
|---|---|---|
| 1 | Megnyitod a webes felületet telefonon/laptopon | Csoportosított kezelőfelület: Vezérlés / Érzékelők / Rendszer |
| 2 | Weben bekapcsolod a **Relé 1**-et | A board LED-je zöldre vált – a kimenet kapcsol |
| 3 | Megnyomod a **BOOT** gombot a boardon | A relé kikapcsol, a weben azonnal frissül az állapot (kétirányú) |
| 4 | Üzemmód → **Automata** (vagy BOOT ≥1,5 s) | A LED kékre vált: a node vár az érzékelőre |
| 5 | Kihúzod a GPIO19–GND jumpert (= ajtó kinyílik) | Relé azonnal BE, LED zöld, weben „Ajtó: nyitva” |
| 6 | Visszadugod (= ajtó becsukódik) | A beállított késleltetés (pl. 5 s) után relé KI |
| 7 | Állítasz a **Lekapcsolási késleltetés** csúszkán, majd újraindítod a boardot | A beállítás és az üzemmód megmarad, a relé KI-ben indul (biztonságos alapállapot) |

**Kulcsüzenet:** a döntés a node-on születik (edge logika) – WiFi vagy szerver kiesésekor is működik;
a web/Home Assistant csak megfigyel és paraméterez.

## Lábkiosztás
| Funkció | Láb |
|---|---|
| RGB LED | GPIO8 |
| BOOT gomb | GPIO9 |
| Relé 1 (vagy LED + 330 Ω) | GPIO18 |
| Ajtó (AH1911 OUT, vagy jumper GND-re) | GPIO19 |

## Home Assistant
Ha van HA: Beállítások → Eszközök → ESPHome integráció automatikusan felajánlja; titkosítási kulcs: `api_key` a `secrets.yaml`-ból.
