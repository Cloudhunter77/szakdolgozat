# ESP32-C6 firmware tervezés – 2026-09-18

Forrás: claude.ai chat „ESP32 C6 firmware tervezés”
(https://claude.ai/chat/f2e78caf-23de-465f-8b83-a81bfaa063c9). A chat egy másik modul kapcsán indult, ide csak
a C6-ra és a Matterre vonatkozó általános megállapítások kerültek.

## C6 korlátok (az architektúrát meghatározzák)
- **Nincs PSRAM**, külső sem támogatott (csak az újabb C61-en van). Egymagos, 160 MHz RISC-V.
  → Nagy pufferigényű feladat (pl. audio stream) a Matter stack mellett nem fér el stabilan.
- **Nincs Classic Bluetooth (BR/EDR)**, csak BLE 5.3 + 802.15.4. A2DP-t nem tud.
- **WiFi csak 2,4 GHz.** Egy 5 GHz-only hálózaton nem párosodik.

## Döntések / megállapítások
- Firmware-alap: **ESP-Matter** (Espressif, `connectedhomeip` fölött).
- A Matter commissioning a hálózati hitelesítő adatokat (WiFi SSID/jelszó) BLE-n adja át a C6-nak. A C6 ezt NVS-ben
  tárolja, és az alkalmazás is eléri. Így egy segédchipnek is továbbadható (pl. I²C-n), és nem kell külön
  provisioning UI.
- I²C master: a C6. Az ESP32 I²C slave módja régebbi IDF-eknél kényes volt. V1-ben egyirányú (C6 → segédchip)
  parancsokkal érdemes indulni.
- Javasolt első lépések: ESP-IDF + ESP-Matter, a `light` példa a C6-on, commissioning, utána saját clusterek.
