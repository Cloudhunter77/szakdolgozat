# Döntésnapló

Állapot: **elfogadva** = Balázs megerősítette · **javaslat** = Claude javasolta, nincs megerősítve ·
**elvetve** = már nem érvényes. Új sor a táblázat aljára. Ha egy döntés megváltozik, a régi sort ne töröld,
hanem állítsd *elvetve*-re, és hivatkozz az újra.

| # | Dátum | Döntés | Indoklás | Állapot | Forrás |
|---|---|---|---|---|---|
| D01 | 2026-09-18 | A központi vezérlő MCU **ESP32-C6** | WiFi 6 + BLE 5.3 + 802.15.4 (Thread) egy chipen, hivatalos Matter SDK | elfogadva | [c6-firmware](beszelgetesek/2026-09-18-c6-firmware-tervezes.md) |
| D02 | 2026-09-18 | A C6 firmware-alapja az **ESP-Matter** (Espressif SDK, `connectedhomeip` alapon) | Gyártói, karbantartott, kész példák | elfogadva | [c6-firmware](beszelgetesek/2026-09-18-c6-firmware-tervezes.md) |
| D03 | 2026-09-30 | Relé: **Schrack 24 V SPDT** (~50 db, kézben) a Songle SRD-24VDC-SL-C helyett | Megbízhatóbb, VDE, megerősített tekercs–érintkező szigetelés a 230 V-os oldalon | javaslat (típuskód függ) | [relek](beszelgetesek/2026-09-30-schrack-relek-io-expander.md) |
| D04 | 2026-09-30 | I/O expander: **TCA9554/PCA9554** a PCF8574 helyett | A PCF8574 bootkor HIGH → a relék meghúznak; a TCA9554 bemenetként indul, push-pull, ESPHome támogatja | javaslat | [relek](beszelgetesek/2026-09-30-schrack-relek-io-expander.md) |
| D05 | 2026-10-02 | Ajtóérzékelés: **AH1911 Hall-kapcsoló + mágnes** a lézeres modul helyett | ~1,6 µA, nincs lézer, egyszerű bekötés, a szakdolgozatban könnyű indokolni | elfogadva (a demó erre épül) | [alkatreszek](beszelgetesek/2026-10-02-alkatreszek-led-ajtoerzekelo.md) |
| D06 | 2026-10-02 | LED-meghajtás új tervben: **logic-level FET** (pl. AO3400A); a nem logic-level FET-ek csak driverrel | 3,3 V-on a nagy FET-ek nem nyitnak ki rendesen | javaslat | [alkatreszek](beszelgetesek/2026-10-02-alkatreszek-led-ajtoerzekelo.md) |
| D07 | 2026-10-09 | Fejlesztés **Linux Mint** alatt, Claude Code-dal a laptopon | – | elfogadva | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D08 | 2026-10-09 | Gyors demó **ESPHome**-mal: helyi (edge) logika a node-on, webes felület, relé bootkor KI | Még aznap bemutatható legyen, HA nélkül is működjön | elfogadva, tesztelve (`cp-01`) | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D09 | 2026-10-09 | Végleges irány: **Matter over Thread**, vezérlő: **Home Assistant** | Balázs otthoni hálózata HA + Thread | elfogadva | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D10 | 2026-10-09 | Matter kiindulás: esp-matter `release/v1.6` `managed_component_light`, ESP-IDF v5.5.5, `esp_matter` ~1.5.0 komponens | Nem kell connectedhomeip klón; a hivatalos CI ugyanígy fordítja a C6 Thread buildet | kiinduló alap | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D11 | 2026-10-09 | Verziókezelés: GitHub, `firmware/` szerkezet, `cp-NN-*` annotált tag csak **hardveren tesztelt** állapotra + `CHECKPOINTS.md` | Visszaállítható, bemutatható mérföldkövek | elfogadva | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D12 | 2026-10-09 | Munkaszabály: **minden módosító lépés előtt kérdezni** | Balázs kérése | elfogadva | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D13 | 2026-10-09 | A megbeszéltek a repóban (`docs/kontextus/`) és a claude.ai Projekt tudástárában is | A Claude Code és a claude.ai chatek ugyanazt a képet lássák | elfogadva | [mai nap](beszelgetesek/2026-10-09-esphome-demo-matter-git.md) |
| D14 | 2026-10-09 | Fejlesztéshez a HA Matter Serverben **test-net DCL** bekapcsolva (teszt PAA/DAC elfogadása) | A példa firmware teszt tanúsítvánnyal (VID 0xFFF1) jelentkezik, enélkül a HA az attesztációnál elutasítja | elfogadva | [NAPLO](NAPLO.md) 2026-10-09 |
