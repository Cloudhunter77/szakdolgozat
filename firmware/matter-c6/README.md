# ModuNode Matter – C6 csatlakoztatása Home Assistantba (Thread)

## 1. Firmware a C6-ra (Claude Code csinálja)
Figyelem: ez felülírja az ESPHome demót (vissza bármikor: `esphome run` a `../esphome-demo` mappában).

Ebben a mappában: *„csináld végig a setup → build → erase → flash lépéseket, aztán nézd meg a boot logot”*.
Első alkalommal kb. 30–45 perc (ESP-IDF telepítés + első Matter build). A sudo-s parancsokat te futtatod.

## 2. Home Assistant előkészítés
1. **Beállítások → Eszközök és szolgáltatások** (*Settings → Devices & services*): legyen fent a **Matter** integráció.
2. *Settings → Connectivity → Thread*: a preferált hálózatnál legyen
   border router (a HA logó jelzi a preferáltat).
3. Thread adatok a telefonra – a HA appban:
   - **Android:** *Settings → Companion app → Troubleshooting* → **Sync Thread credentials**
   - **iPhone:** *Settings → Connectivity → Thread* → **Send credentials to phone**
4. **Csak Androidon:** a teszt eszközt fel kell venni a Google Home Developer Console-ban
   (console.home.google.com, ugyanazzal a Google fiókkal, ami a telefonon van): új projekt → Matter integráció →
   **Vendor ID: 0xFFF1 (teszt)**, **Product ID: 0x8000**. Enélkül Androidon elhasal a párosítás.
   A *Product name* és a *Device type* (Light) is kötelező, utána **Save** – kész, ha „Ready to test”-et ír.
5. **Teszt tanúsítvány elfogadása:** *Settings → Add-ons → Matter Server → Configuration* →
   **Enable test-net DCL usage** be → Save → az add-on **Restart**. Enélkül a HA az eszköz-hitelesítésnél
   (attesztáció) elutasítja a fejlesztői firmware-t („error code 1”).

## 3. Párosítás
1. Bluetooth be, telefon a C6 és a border router közelében.
2. HA app → *Settings → Connectivity → Matter* → **Add device** → *„No. It's new.”*
3. Olvasd be a `matter-qr.png`-t, vagy add meg kézzel: **3497-011-2332**.
4. iPhone-on *„Uncertified Accessory”* → **Add Anyway**.
5. Pár perc. A végén megjelenik egy lámpa entitás.

## 4. Teszt
- HA-ban a lámpa ki/be, fényerő, szín → a board RGB LED-je követi.
- BOOT gomb rövid nyomás → a HA-ban azonnal frissül az állapot.
- BOOT 5 mp nyomva tartás → gyári visszaállítás (törlődik a HA-ból, újra párosítható).
