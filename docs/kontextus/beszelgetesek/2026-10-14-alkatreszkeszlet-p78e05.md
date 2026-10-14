# Alkatrészkészlet átnézése, a modulmag tápja: P78E05 – 2026-10-13/14

Forrás: claude.ai chat, a `2026-10-02-alkatreszek-led-ajtoerzekelo.md` chat folytatása (2026-10-13 délután –
2026-10-14). Döntések: **D56, D57** a `DONTESEK.md`-ben. Ennek nyomán frissítve: `../MODULMAG-SPEC.md`
(2. fejezet), `../SAMPLE-KERESEK.md`, `../NYAK-ELOKESZITES.md`, `../ATTEKINTES.md`.

## Készlet-átnézés (Balázs fotói + a „Csőtárak raktárban” táblázat)
Az aktuális terv (D27–D55, `MODULMAG-SPEC.md`) szemével.

**Jól jön:**

| Alkatrész | Db | Mire |
|---|---|---|
| **P78E05-1000** (CUI/Bel, 8–36 V → 5 V, 1 A, SIP-3, a 7805 lábkiosztásával) | ~200 | a modulmag tápja → **D56** |
| **NCP1117ST33T3G** (onsemi LDO, 3,3 V, SOT-223, bemenet max. 20 V) | tekercs (~350) | 5 V → 3,3 V a P78E05 után; csak egy 5 V-os fokozat után mehet |
| **LM2576S** (3 A-es buck) | 45 | 24 V-ról 5 V vagy 12 V, ha kell; a végződést ellenőrizni (-5.0 / -12 / -ADJ): a sima 40 V-ig, a HV 60 V-ig bírja |
| **ACS758LCB-100B** (Hall-áramérzékelő, ±100 A, 3–5,5 V, ratiometrikus, 4800 Vrms) | – | alternatíva a LED-modul össz-áramára a sönt + INA181 helyett; 3,3 V-on ~13 mV/A → 15–20 A-hez elég, de durva; nagy, furatszerelt tok. **A D53 (sönt + INA181A2) marad** |
| **LM2904 / LM2902** (2/4 műveleti erősítő, a bemenet a GND-ig ér) | – | alsó oldali söntes árammérés; 5 V-ról, a kimenetet az ADC-tartományhoz igazítani |
| **IRFR1205** (55 V, 27 mΩ, DPAK) | – | tartalék LED-FET ugyanarra a DPAK footprintre (az NTD5C648NL / IPD053N06N helyett); 10 A-en ~2,7 W → nagy rézfelület kell |
| **WS2812C-2020** + **74HCT14D** | – / 36 | állapot-LED ötlet: a WS2812C-nek ≥ 3,7 V kell (az 5 V-os sín), a 74HCT14 két sorba kötött inverterrel emeli a 3,3 V-os jelet. Nem része a v1-nek (a PC13-as LED marad) |
| **LH1522-AAC** (photoMOS relé) | 100 | kis áramú, potenciálmentes kimenet (pl. kazán-termosztát, kapunyitó) – nem a 4 panelhez |
| **LM3940 3,3 V** | 19 | 5 → 3,3 V LDO, az NCP1117 helyett is |
| **BT137** (triac) | ~400 | csak egy későbbi 230 V-os dimmer modulhoz |

**Nem kell:** PIC16F883, PIC18F2431, PIC16LF876A (van STM32) · 24C02C (csak 5 V-os, a flash kiváltja) ·
74HC541, ACT541, LCX541, ACT573, ALUC244 (buszmeghajtók) · 74LVC2G14 · SP34063 (a UCC27524 12 V-ja lineárisan
jön, MC78L12) · a táblázat telekom- és retró alkatrészei (MC68A09/MC68A50, EF68A21, 8255, MC146818, DTMF-vevők,
ISD hangrögzítők, PCM-codec, 74LS, CD4066, TL072, HCNR200, optocsatolók, N82S141).

## Döntés: a modulmag tápja P78E05 + NCP1117 (D56)
- A kérdés: a modulmag 60 V-os buckja (LMR36006, TI-sample) maradjon, vagy a P78E05 kerüljön bele? Claude az
  LMR36006-ot javasolta (nagyobb tüsketartalék), a P78E05-öt B-tervnek. Balázs: „van vagy 200 db a p78e05-ből,
  úgyhogy szerintem az lesz”.
- Előny: kézben van, kész modul (nincs tekercs, buck-layout, VQFN-reflow), nem függ a TI-sample-től.
- Táplánc: 24 V → F1 → SS16 → (R6) → SMBJ28A + **C12 elkó** + 10 µF → **P78E05** → 5 V (22 µF) →
  **NCP1117ST33** → 3,3 V (10 µF tantál). Részletek: `MODULMAG-SPEC.md` 2. fejezet.
- Az 1 A-es 5 V bőven elég (a modulmag < 100 mA); az NCP1117-en (5 − 3,3) V × 0,1 A ≈ 0,17 W.
- **P78E05 adatlap** (P78E-1000 sorozat, rev. 1.01): 8–36 V be, 5 V (±1,5 % tip., ±3 % max.), 1 A, 93 %
  (min. Vin, teljes terhelés), üresjárás ~0,3 mA, 75 mVp-p hullámosság, rövidzár-védett (automatikus
  visszaállás). Külső kondenzátorok: 10 µF / 50 V be, 22 µF / 10 V ki; 30 V feletti bemenetnél 22 µF / 50 V-os
  bemeneti kondenzátor kötelező; max. kapacitív terhelés 680 µF. 11,6 × 8,0 × 10,4 mm, −40 … 85 °C.
  **Abszolút maximum nincs megadva → 36 V a határ.**
- **NCP1117:** abs. max. 20 V a bemeneten, ejtés 100 mA-en max. 1,1 V; a kimeneten min. 4,7 µF, ESR ~33 mΩ–2,2 Ω
  → tantál, vagy kerámia + kis soros ellenállás (egy tiszta kerámia ESR-je az alsó határ alatt lehet).
- **A vezérlőn (D46) egyelőre marad a két buck** – nyitott, hogy ott is P78E05 legyen-e:
  - V_BUS: 5,0 V ± 3 % → a TPS2553, a kábel és a modul PTC-je után legrosszabb esetben ~4,7 V a modulon; az ISO1042
    VCC2-jének 4,5 V kell → szűken, de belefér (a D46 5,2 V-ot javasolt).
  - 3,3 V a C6 + W5500-nak: 5 V-ról LDO-val a D46 indoklása szerint túl melegedne → ott buck kell.

## Védelem (D57)
- A tüske-veszély a modul **24 V-os betápján** van (sorkapocs bedugása üzem közben, hosszú betápkábel).
  *Javítás a chathez:* ott a JST-bedugást említettük, de a láncon D28 óta nincs 24 V, csak a V_BUS 5 V-ja.
- Csak kerámia bemeneti kondenzátorral a kábel induktivitása LC-kört alkot → bedugáskor a feszültség a 24 V
  közel kétszereséig (~48 V) lenghet. A **47 µF / 50 V-os elkó** ESR-je ezt csillapítja → **kötelező** (C12;
  egyben a P78E05 adatlapja szerinti bemeneti kondenzátor).
- **SMBJ28A** (Vbr 31,1–34,4 V): kis áramnál ~31–35 V-on fog, teljes impulzusáramnál ~45 V-on → a 36 V-os
  P78E05-nek önmagában csak kiegészítő védelem. Javaslat: **R6 = 10 Ω** (1206, impulzusbíró) a D1 után → a C12-vel
  ~0,5 ms-os RC-szűrő, a TVS árama korlátozott, így kis áramon, 36 V alatt fog. Esés üzemben ~0,25 V (~25 mA a
  24 V-os oldalon). 0 Ω-mal áthidalható.
- A 24 V-os tápot **ne állítsd 26 V fölé**.

## Nyitott
- D46: P78E05 a vezérlőn is (V_BUS)?
- A sample-lista frissítve: az LMR36006 és a 10 µH-s tekercs már csak a vezérlőhöz kell.
- `MODULMAG-SPEC.md` 11.: a P78E05 (10,4 mm) és a C12 elkó magassága a DIN-ház vállmagassága alatt; a P78E05
  KiCad-footprintje (SIP-3, 2,54 mm).

## Források
- [P78E-1000 sorozat adatlap (CUI)](https://static.chipdip.ru/lib/309/DOC011309445.pdf)
- [NCP1117 adatlap (onsemi)](https://static.chipdip.ru/lib/487/DOC011487346.pdf)
- [ACS758 adatlap (Allegro)](https://datasheet.octopart.com/ACS758LCB-100B-PFF-T-Allegro-datasheet-10031246.pdf)
