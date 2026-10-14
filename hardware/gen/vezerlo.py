"""Vezérlő – first draft from docs/kontextus/VEZERLO-SPEC.md."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Vezérlő – ESP32-C6-WROOM-1 + W5500 + CAN + V_BUS', 'vezerlo', paper='A2')
ML = '/home/balazs/dev/szakdolgozat/hardware/lib/modularis.kicad_sym'
for n in ('LMR36015BRNXR', 'TPS2553DBV', 'ESP32-C6-WROOM-1'):
    S.use(f'modularis:{n}', lib='modularis', name=n, libpath=ML)
S.label_dx.update({'modularis:ESP32-C6-WROOM-1': 22.86, 'Interface_Ethernet:W5500': 22.86,
                   'modularis:LMR36015BRNXR': 12.7, 'modularis:TPS2553DBV': 12.7,
                   'Converter_DCDC:R-78E5.0-1.0': 10.16, 'Interface_CAN_LIN:MCP2562-E-SN': 12.7,
                   'Connector:RJ45_Hanrun_HR911105A_Horizontal': 25.4,
                   'Connector:USB_C_Receptacle_USB2.0_16P': 12.7, 'Power_Protection:USBLC6-2SC6': 10.16,
                   'Connector_Generic:Conn_01x04': 5.08, 'Connector_Generic:Conn_01x06': 5.08,
                   'Connector_Generic:Conn_01x02': 5.08, 'Device:Crystal_GND24': 5.08,
                   'Power_Protection:NUP2105L': 5.08, 'LED:WS2812B': 7.62, '74xx:74HC14': 7.62})
R0603, C0603 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric'

def N(note, k):
    if note:
        k.setdefault('props', {})['Megjegyzés'] = note
    return k

def R(ref, val, x, y, a, b, fp=R0603, note=None, **k):
    S.comp('Device:R', ref, val, x, y, {'1': a, '2': b}, fp=fp, **N(note, k))

def C(ref, val, x, y, a, b, fp=C0603, note=None, **k):
    S.comp('Device:C', ref, val, x, y, {'1': a, '2': b}, fp=fp, **N(note, k))

def D(ref, val, x, y, a, k_, fp, sym='Device:D_Schottky', r=0, note=None):
    S.comp(sym, ref, val, x, y, {'2': a, '1': k_}, fp=fp, r=r, **N(note, {}))

def TP(ref, net, x, y):
    S.comp('Connector:TestPoint', ref, net, x, y, {'1': net}, fp='TestPoint:TestPoint_Pad_D1.5mm')

# ======================= 2.1 bemenet, USB-ág =======================
S.text('2.1 BEMENET: +24V_IN → F1 → D1 → +24V_P;  USB csak a 3,3 V-os buckot táplálja (D3) – a V_BUS USB-ről hardveresen KI (D61)', 20, 25, 2)
y = 45
S.comp('Connector_Generic:Conn_01x02', 'J1', '24V IN', 20, y, {'1': '+24V_IN', '2': 'GND'},
       fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal',
       props={'Megjegyzés': 'push-in sorkapocs – a típus a DIN-ház vállához (D50)'})
S.comp('Device:Fuse', 'F1', '1A', 40, y, {'1': '+24V_IN', '2': '+24V_F1'}, fp='Fuse:Fuse_1206_3216Metric',
       props={'Megjegyzés': '≥ 32 V, gyors'})
D('D1', 'SS16', 55, y, '+24V_F1', '+24V_P', 'Diode_SMD:D_SMA')
D('D2', 'SMBJ28A', 70, y, 'GND', '+24V_P', 'Diode_SMD:D_SMB', sym='Device:D_Zener', r=90)
R('R1', '150k', 85, y, '+24V_P', 'VIN_SENSE')
R('R2', '10k', 97, y, 'VIN_SENSE', 'GND')
C('C3', '100n', 109, y, 'VIN_SENSE', 'GND')
D('D8', 'SS16', 125, y, '+24V_P', 'VIN_BUCK', 'Diode_SMD:D_SMA', note='az USB ne táplálja vissza a 24 V-os oldalt')
D('D3', 'B360', 145, y, 'VUSB', 'VIN_BUCK', 'Diode_SMD:D_SMC', note='60 V-os kell (túlfeszültségnél VIN_BUCK ~45 V, VUSB ~0 V)')
R('R7', '10R', 165, y, '+24V_P', '+24V_F', fp='Resistor_SMD:R_2512_6332Metric', note='impulzusbíró, 2512; 0 Ω-mal áthidalható (D57)')
D('D7', 'SMBJ28A', 180, y, 'GND', '+24V_F', 'Diode_SMD:D_SMB', sym='Device:D_Zener', r=90)
S.comp('Device:C_Polarized', 'C1', '47µ/50V', 195, y, {'1': '+24V_F', '2': 'GND'}, fp='Capacitor_SMD:CP_Elec_6.3x7.7',
       props={'Megjegyzés': 'elektrolit, low-ESR, 105 °C – KÖTELEZŐ (D57)'})
C('C2', '10µ/50V', 210, y, '+24V_F', 'GND', fp='Capacitor_SMD:C_1210_3225Metric')
# 2.3 P78E05
S.comp('Converter_DCDC:R-78E5.0-1.0', 'U2', 'P78E05-1000', 235, y, {'1': '+24V_F', '2': 'GND', '3': '+5V'},
       fp='Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT')
C('C13', '22µ/10V', 262, y, '+5V', 'GND', fp='Capacitor_SMD:C_1206_3216Metric')

# ======================= 2.2 LMR36015 → 3V3 =======================
S.text('2.2 3,3 V – LMR36015BRNXR (1 MHz): FOOTPRINT a TI Ultra Librarian-ből!', 20, 75, 2)
y = 100
S.comp('modularis:LMR36015BRNXR', 'U1', 'LMR36015BRNXR', 70, y,
       {'2': 'VIN_BUCK', '10': 'VIN_BUCK', '9': 'VIN_BUCK', '5': 'BUCK_VCC', '1': 'GND', '11': 'GND', '6': 'GND',
        '4': 'BUCK_BOOT', '12': 'BUCK_SW', '3': 'BUCK_SW', '7': 'BUCK_FB', '8': 'GND'})
C('C4', '4µ7/50V', 25, y, 'VIN_BUCK', 'GND', fp='Capacitor_SMD:C_1210_3225Metric')
C('C5', '220n/50V', 35, y, 'VIN_BUCK', 'GND', note='a 2-es VIN-lábnál')
C('C6', '220n/50V', 45, y, 'VIN_BUCK', 'GND', note='a 10-es VIN-lábnál')
C('C7', '100n', 105, y - 10, 'BUCK_BOOT', 'BUCK_SW')
C('C8', '1µ/16V', 105, y + 10, 'BUCK_VCC', 'GND', note='VCC–AGND, más terhelés nem mehet rá')
S.comp('Device:L', 'L1', '6,8µH', 120, y, {'1': 'BUCK_SW', '2': '+3V3'}, fp='Inductor_SMD:L_Coilcraft_XAL5030-XXX',
       props={'Megjegyzés': 'árnyékolt, Isat ≥ 2,1 A (ideálisan ≥ 2,8 A), ~5 × 5 mm'})
R('R3', '100k 1%', 135, y, '+3V3', 'BUCK_FB')
C('C9', '20p', 145, y, '+3V3', 'BUCK_FB', note='CFF, R3-mal párhuzamosan')
R('R4', '43,2k 1%', 155, y, 'BUCK_FB', 'GND', note='→ 3,31 V (VFB = 1,0 V)')
for i, x in enumerate((170, 182, 194)):
    C(f'C{10 + i}', '22µ/10V', x, y, '+3V3', 'GND', fp='Capacitor_SMD:C_1206_3216Metric')

# ======================= 2.4 TPS2553 → V_BUS =======================
S.text('2.4 V_BUS – TPS2553: EN osztó a +24V_P-ről (csak 24 V mellett BE), GPIO20 BAT54-en át letiltja', 230, 75, 2)
y = 100
S.comp('modularis:TPS2553DBV', 'U3', 'TPS2553DBVR', 270, y,
       {'1': '+5V', '3': 'VBUS_EN_IN', '5': 'VBUS_ILIM', '2': 'GND', '6': 'V_BUS', '4': 'VBUS_FAULT'})
C('C22', '1µ', 235, y, '+5V', 'GND')
C('C23', '100n', 245, y, '+5V', 'GND')
R('R10', '470k', 235, y + 25, '+24V_P', 'VBUS_EN_IN')
R('R11', '47k', 247, y + 25, 'VBUS_EN_IN', 'GND')
D('D9', 'BAT54WS', 260, y + 25, 'VBUS_EN_IN', 'VBUS_EN', 'Diode_SMD:D_SOD-323', note='anód az EN-en, katód a GPIO20-on')
R('R12', '61,9k 1%', 285, y + 25, 'VBUS_ILIM', 'GND', note='→ 382/425/476 mA')
R('R34', '10k', 300, y + 25, '+3V3', 'VBUS_FAULT', note='FAULT felhúzás (nyitott drain)')
C('C24', '100n', 300, y, 'V_BUS', 'GND')
C('C25', '10µ/16V', 312, y, 'V_BUS', 'GND', fp='Capacitor_SMD:C_0805_2012Metric')
D('D4', 'SMF5.0A', 325, y, 'GND', 'V_BUS', 'Diode_SMD:D_SOD-123F', sym='Device:D_Zener', r=90)
R('R13', '100k', 340, y, 'V_BUS', 'VBUS_SENSE')
R('R14', '22k', 352, y, 'VBUS_SENSE', 'GND')
C('C14', '100n', 364, y, 'VBUS_SENSE', 'GND')

# ======================= 3. ESP32-C6-WROOM-1 =======================
S.text('3. ESP32-C6-WROOM-1-N16 (fém szekrénybe -1U – az EPAD helyét ellenőrizni!)', 20, 145, 2)
x0, y0 = 110, 200
S.comp('modularis:ESP32-C6-WROOM-1', 'U4', 'ESP32-C6-WROOM-1-N16', x0, y0,
       {'1': 'GND', '28': 'GND', '29': 'GND', '2': '+3V3', '3': 'CHIP_EN', '4': 'GPIO4', '5': 'GPIO5',
        '6': 'SPI_SCLK_C6', '7': 'SPI_MOSI', '8': 'VIN_SENSE', '9': 'VBUS_SENSE', '10': 'RGB_DIN_3V3',
        '11': 'W5500_CS', '12': 'W5500_RST', '13': 'USB_DM', '14': 'USB_DP', '15': 'BOOT', '16': 'CAN_TX',
        '17': 'CAN_RX', '18': 'VBUS_EN', '19': 'VBUS_FAULT', '20': 'GPIO22', '21': 'GPIO23', '23': 'GPIO15',
        '24': 'U0RXD', '25': 'U0TXD_C6', '26': 'W5500_INT', '27': 'SPI_MISO'}, nc=['22'])
C('C26', '22µ', 30, 170, '+3V3', 'GND', fp='Capacitor_SMD:C_0805_2012Metric', note='a 3V3-lábnál')
C('C27', '100n', 40, 170, '+3V3', 'GND', note='a 3V3-lábnál')
R('R15', '10k', 30, 195, '+3V3', 'CHIP_EN')
C('C15', '1µ', 40, 195, 'CHIP_EN', 'GND', note='RC-késleltetés az EN-en')
R('R16', '10k', 50, 195, '+3V3', 'BOOT')
R('R17', '10k', 60, 195, '+3V3', 'RGB_DIN_3V3', note='strapping: letöltéshez GPIO8 = 1')
R('R18', '10k', 70, 195, '+3V3', 'GPIO15')
R('R35', '10k', 30, 220, '+3V3', 'CAN_TX', note='reset alatt recesszív busz')
R('R36', '10k', 40, 220, '+3V3', 'W5500_CS')
R('R37', '10k', 50, 220, '+3V3', 'W5500_RST')
R('R38', '10k', 60, 220, '+3V3', 'W5500_INT')
R('R19', '0R', 160, 160, 'SPI_SCLK_C6', 'SPI_SCLK', note='33 Ω-hoz footprint')
C('C28', 'DNP', 172, 160, 'SPI_SCLK', 'GND', dnp=True, note='kondenzátor-footprint, nem beültetve')
R('R39', '499R', 160, 245, 'U0TXD_C6', 'U0TXD', note='Espressif-ajánlás')
for i, n in enumerate(('GPIO4', 'GPIO5', 'GPIO22', 'GPIO23')):
    TP(f'TP{i + 1}', n, 30 + i * 10, 245)

# ======================= 4. W5500 =======================
S.text('4. ETHERNET – W5500 + HR911105A MagJack (opcionálisan beültetve; MDI a WIZnet use_mag referencia szerint)', 230, 145, 2)
x0, y0 = 300, 210
w = {'1': 'ETH_TXN', '2': 'ETH_TXP', '5': 'ETH_RXN', '6': 'ETH_RXP', '10': 'W_EXRES', '20': 'W_TOCAP',
     '22': 'W_1V2O', '23': 'GND', '25': 'ETH_LED_LINK', '27': 'ETH_LED_ACT', '28': '+3V3', '29': 'GND',
     '30': 'XTAL25_I', '31': 'XTAL25_O', '32': 'W5500_CS', '33': 'SPI_SCLK', '34': 'SPI_MISO', '35': 'SPI_MOSI',
     '36': 'W5500_INT', '37': 'W5500_RST'}
for p in ('3', '9', '14', '16', '19', '48'):
    w[p] = 'GND'
for p in ('4', '8', '11', '15', '17', '21'):
    w[p] = '+3V3A'
S.comp('Interface_Ethernet:W5500', 'U5', 'W5500', x0, y0, w,
       nc=['7', '12', '13', '46', '47', '18', '24', '26', '38', '39', '40', '41', '42', '43', '44', '45'])
S.text('VBG (18) NYITVA · RSVD 38–42 NYITVA · RSVD 23 GND · PMODE nyitva (auto-negotiation)', 260, 255)
R('R40', '12,4k 1%', 250, 270, 'W_EXRES', 'GND')
C('C29', '4µ7', 262, 270, 'W_TOCAP', 'GND', fp='Capacitor_SMD:C_0805_2012Metric')
C('C30', '10n', 274, 270, 'W_1V2O', 'GND')
S.comp('Device:FerriteBead_Small', 'FB1', '120R@100MHz', 290, 270, {'1': '+3V3', '2': '+3V3A'},
       fp='Inductor_SMD:L_0603_1608Metric', props={'Megjegyzés': 'HH-1M1608-121JT, ≥ 300 mA'})
for i in range(6):
    C(f'C{31 + i}', '100n', 305 + i * 10, 270, '+3V3A', 'GND', note='AVDD-lábanként')
C('C37', '100n', 365, 270, '+3V3', 'GND', note='VDD (28)')
C('C38', '10µ', 375, 270, '+3V3', 'GND', fp='Capacitor_SMD:C_0805_2012Metric')
C('C39', '10µ', 385, 270, '+3V3A', 'GND', fp='Capacitor_SMD:C_0805_2012Metric')
S.comp('Device:Crystal_GND24', 'Y1', '25MHz ±30ppm', 250, 175, {'1': 'XTAL25_I', '3': 'XTAL25_O', '2': 'GND', '4': 'GND'},
       fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
C('C40', '18p', 240, 190, 'XTAL25_I', 'GND', note='C = 2 × (CL − 3…5 pF) a megvett kvarcból')
C('C41', '18p', 262, 190, 'XTAL25_O', 'GND')
# MDI
R('R20', '49,9R 1%', 360, 160, 'ETH_TXP', '+3V3A')
R('R21', '49,9R 1%', 372, 160, 'ETH_TXN', '+3V3A')
C('C16', '10n', 384, 160, '+3V3A', 'GND', note='a TXB csomópontnál')
R('R22', '49,9R 1%', 360, 185, 'ETH_RXP', 'ETH_RXB')
R('R23', '49,9R 1%', 372, 185, 'ETH_RXN', 'ETH_RXB')
C('C17', '6,8n', 384, 185, 'ETH_RXB', 'GND', note='a RXB csak kondenzátoron át a GND-re, NEM a 3,3 V-ra')
R('R24', '10R 1%', 400, 160, '+3V3A', 'ETH_TCT')
C('C18', '22n', 412, 160, 'ETH_TCT', 'GND')
C('C19', '6,8n', 412, 185, 'ETH_RCT', 'GND')
S.comp('Connector:RJ45_Hanrun_HR911105A_Horizontal', 'J6', 'HR911105A', 450, 210,
       {'1': 'ETH_TXP', '2': 'ETH_TXN', '3': 'ETH_RXP', '6': 'ETH_RXN', '4': 'ETH_TCT', '5': 'ETH_RCT',
        '8': 'GND', '9': 'ETH_LED_G_A', '10': 'ETH_LED_LINK', '12': 'ETH_LED_Y_A', '11': 'ETH_LED_ACT',
        'SH': 'ETH_SHIELD'}, nc=['7'],
       props={'Megjegyzés': 'a lábkiosztást a megvett darab adatlapjából ellenőrizni (TCT és RCT külön lábon)'})
R('R41', '330R', 430, 245, '+3V3', 'ETH_LED_G_A', note='zöld = link')
R('R42', '330R', 442, 245, '+3V3', 'ETH_LED_Y_A', note='sárga = aktivitás')
C('C20', '1n/2kV', 470, 245, 'ETH_SHIELD', 'GND', fp='Capacitor_SMD:C_1206_3216Metric')

# ======================= 5. CAN, 6. busz =======================
S.text('5–6. CAN – TCAN1044AVDRQ1 (MCP2562 szimbólum, lábról lábra azonos) · JP2 alap 5V: 1044/2562 · 3V3: 330/230', 230, 300, 2)
y = 340
S.comp('Interface_CAN_LIN:MCP2562-E-SN', 'U6', 'TCAN1044AVDRQ1', 280, y,
       {'1': 'CAN_TX', '2': 'GND', '3': 'CAN_VCC', '4': 'CAN_RX', '5': 'CAN_VIO', '6': 'CAN_L', '7': 'CAN_H', '8': 'CAN_STB'},
       fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
S.comp('Jumper:SolderJumper_3_Bridged12', 'JP2', 'VCC: 1-2=5V / 2-3=3V3', 240, 325, {'1': '+5V', '2': 'CAN_VCC', '3': '+3V3'},
       fp='Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',
       props={'Megjegyzés': 'SOHA ne legyen mindkét oldal összeforrasztva!'})
S.comp('Jumper:SolderJumper_3_Bridged12', 'JP3', 'VIO: 1-2=3V3 / 2-3=GND', 240, 355, {'1': '+3V3', '2': 'CAN_VIO', '3': 'GND'},
       fp='Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm', props={'Megjegyzés': 'SN65HVD230-nál nyitva'})
C('C42', '100n', 255, 375, 'CAN_VCC', 'GND')
C('C43', '1µ', 265, 375, 'CAN_VCC', 'GND')
C('C44', '100n', 275, 375, 'CAN_VIO', 'GND')
R('R43', '0R', 300, 375, 'CAN_STB', 'GND', note='STB → normál mód (nyitva készenlét!)')
S.comp('Power_Protection:NUP2105L', 'U7', 'ESD2CAN24-Q1', 330, 375, {'1': 'CAN_L', '2': 'CAN_H', '3': 'GND'})
S.comp('Jumper:Jumper_2_Open', 'JP1', 'LEZÁRÁS', 350, 375, {'1': 'CAN_H', '2': 'CAN_TERM'},
       fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
R('R25', '120R', 365, 375, 'CAN_TERM', 'CAN_L', fp='Resistor_SMD:R_0805_2012Metric')
bus = {'1': 'V_BUS', '2': 'GND', '3': 'CAN_L', '4': 'CAN_H'}
S.comp('Connector_Generic:Conn_01x04', 'J2', 'BUS (XH)', 400, 335, bus, fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
S.comp('Connector_Generic:Conn_01x04', 'J3', 'BUS (XH)', 400, 365, bus, fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')

# ======================= 7. USB-C =======================
S.text('7. USB-C – csak eszköz, csak táp-fogyasztó (CC1/CC2 külön 5,1 kΩ)', 20, 300, 2)
S.comp('Connector:USB_C_Receptacle_USB2.0_16P', 'J4', 'USB-C 16P', 45, 350,
       {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'A4': 'VUSB', 'A9': 'VUSB', 'B4': 'VUSB', 'B9': 'VUSB',
        'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_DP_CONN', 'B6': 'USB_DP_CONN', 'A7': 'USB_DM_CONN',
        'B7': 'USB_DM_CONN', 'SH': 'GND'}, nc=['A8', 'B8'], fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12')
R('R28', '5,1k', 85, 330, 'USB_CC1', 'GND')
R('R29', '5,1k', 95, 330, 'USB_CC2', 'GND')
R('R30', '2,2k', 105, 330, 'VUSB', 'GND', note='levezető: a D3 szivárgása ne húzza fel a kihúzott aljzat VBUS-át')
C('C21', '1µ', 115, 330, 'VUSB', 'GND')
S.comp('Power_Protection:USBLC6-2SC6', 'U8', 'USBLC6-2SC6', 100, 370,
       {'1': 'USB_DP_CONN', '6': 'USB_DP_CONN', '3': 'USB_DM_CONN', '4': 'USB_DM_CONN', '5': 'VUSB', '2': 'GND'})
R('R26', '22R', 135, 360, 'USB_DP_CONN', 'USB_DP', note='a C6 közelében')
R('R27', '22R', 145, 360, 'USB_DM_CONN', 'USB_DM', note='a C6 közelében')

# ======================= 8. kezelőszervek, LED-ek, debug =======================
S.text('8. GOMBOK, LED-EK, DEBUG – U9 és R32 egyszerre NE legyen beültetve', 430, 300, 2)
S.comp('Switch:SW_Push', 'SW1', 'RESET', 440, 320, {'1': 'CHIP_EN', '2': 'GND'}, fp='Button_Switch_SMD:SW_SPST_TL3342')
S.comp('Switch:SW_Push', 'SW2', 'BOOT', 460, 320, {'1': 'BOOT', '2': 'GND'}, fp='Button_Switch_SMD:SW_SPST_TL3342')
R('R44', '2,2k', 480, 320, '+3V3', 'LED_PWR')
S.comp('Device:LED', 'D5', 'zöld', 492, 320, {'2': 'LED_PWR', '1': 'GND'}, fp='LED_SMD:LED_0603_1608Metric', r=90)
S.comp('74xx:74HC14', 'U9', '74HCT14D', 445, 350, {'1': 'RGB_DIN_3V3', '2': 'RGB_HCT_MID'}, unit=1,
       fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')
S.comp('74xx:74HC14', 'U9', '74HCT14D', 470, 350, {'3': 'RGB_HCT_MID', '4': 'RGB_DIN_5V'}, unit=2,
       fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')
for u, (a, yy) in enumerate((('5', '6'), ('9', '8'), ('11', '10'), ('13', '12')), start=3):
    S.comp('74xx:74HC14', 'U9', '74HCT14D', 495 + (u - 3) * 18, 350, {a: 'GND'}, nc=[yy], unit=u,
           fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')
S.comp('74xx:74HC14', 'U9', '74HCT14D', 170, 330, {'14': '+5V', '7': 'GND'}, unit=7,
       fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')
C('C45', '100n', 185, 330, '+5V', 'GND', note='U9 VCC')
R('R31', '33R', 198, 330, 'RGB_DIN_5V', 'RGB_DIN')
R('R32', '0R', 211, 330, 'RGB_DIN_3V3', 'RGB_DIN', dnp=True, note='DNP – csak ha az U9 nincs beültetve (WS2812B-V5 3,3 V-os bemenettel)')
S.comp('LED:WS2812B', 'D6', 'WS2812B-V5', 180, 365, {'1': '+5V', '3': 'GND', '4': 'RGB_DIN'}, nc=['2'])
C('C46', '100n', 205, 365, '+5V', 'GND', note='D6 VDD')
S.comp('Connector_Generic:Conn_01x06', 'J5', 'DEBUG', 540, 320,
       {'1': 'J5_VREF', '2': 'GND', '3': 'U0TXD', '4': 'U0RXD', '5': 'CHIP_EN', '6': 'BOOT'},
       fp='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
R('R33', '0R', 520, 320, '+3V3', 'J5_VREF', dnp=True, note='DNP – csak referencia, különben az USB-UART visszatáplál')

# ======================= PWR_FLAG-ek =======================
for i, n in enumerate(['GND', '+3V3', '+24V_P', '+24V_F', 'VIN_BUCK', '+3V3A', 'CAN_VCC', 'CAN_VIO', 'VUSB']):
    S.flag(n, 240 + i * 14, 398)
S.text('VÁZLAT – generálva a VEZERLO-SPEC.md alapján (2026-10-14). Elrendezést rendezd; a bekötés címkékkel kész.', 20, 405, 1.5)
S.write(OUT)
print('ok', OUT)
