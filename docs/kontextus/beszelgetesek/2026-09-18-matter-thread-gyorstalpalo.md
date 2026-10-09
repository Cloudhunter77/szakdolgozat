# Matter over Thread gyorstalpaló – 2026-09-18

Forrás: claude.ai chat „Matter over Thread protokoll gyorstalpaló”
(https://claude.ai/chat/52dba945-9f52-47bf-a0d2-a21afd959797). A teljes, kb. 30 perces anyag egy Claude Docban van.

## Lényeg
- **Thread** = szállítás: IEEE 802.15.4 (2,4 GHz) mesh, IPv6 6LoWPAN-on. Szerepek: Leader, Router, REED,
  végeszközök (MED, SED). A **Border Router** köti össze a Thread hálót az otthoni IP hálózattal.
- **Matter** = alkalmazási nyelv, a CSA (volt Zigbee Alliance) szabványa. Ugyanaz fut Threaden, WiFi-n és Etherneten.
  UDP fölött, saját megbízhatósági réteggel (MRP).
- **Adatmodell:** Node → Endpoint → Cluster → Attribute / Command. A Device Type megadja, mely clusterek
  kötelezőek (pl. Dimmable Light, Contact Sensor).
- **Párosítás (commissioning):** BLE felfedezés → PASE (setup kód) → eszköz-attesztáció (DAC) → hálózati
  hitelesítő adatok átadása (WiFi SSID/jelszó vagy Thread dataset) → operatív felfedezés → CASE → NOC kiadás.
- **Biztonság:** Fabric = egy vezérlő „világa”. Multi-admin: egy eszköz több fabricben is lehet (pl. HA + Apple Home).
- 2026-os helyzet: Matter 1.6, Thread 1.4 tanúsítási követelmények.

## Saját eszköz fejlesztése – ajánlások
- Belépési utak: connectedhomeip referencia SDK · gyártói SDK (**ESP-Matter**, nRF Connect SDK) · Zephyr + OpenThread.
- Hardverigény: kb. 250–320 KB RAM, 1 MB+ flash, BLE + 802.15.4 rádió, hardveres kriptó.
- Chipek: **ESP32-C6** (WiFi + Thread, olcsó, hivatalos SDK) · ESP32-H2 (csak Thread) · nRF52840 / nRF54L15 ·
  EFR32MG24.
- Menet: dev boardon validálás, csak utána saját NYÁK. Először egy példa app (light), commissioning, utána testreszabás.
- Hobbi/szakdolgozat szinten a teszt DAC (VID 0xFFF1) elég. Tanúsítás csak kereskedelmi termékhez kell.
