"""STM32CubeMX-projektek (.ioc) a három modulhoz – a MODULMAG-SPEC 7. fejezetének lábkiosztásából.

Használat: python3 hardware/gen/cubemx.py  →  hardware/cubemx/<modul>/<modul>.ioc
A CubeMX-ben megnyitva a lábak a jelükkel és a címkéjükkel jelennek meg; ha egy jel nem rendelhető a lábhoz, vagy két
funkció ütközik, a CubeMX jelzi. MCU: STM32L433RCT3 (D78); a jel- és üzemmódnevek a CubeMX 6.18 adatbázisából
(STM32L433R(B-C)Tx.xml, IP/*.xml). A DAC/COMP/ADC-belső kapcsolatokat (COMP2 → TIM1/TIM15/TIM16 BKIN, DAC1 → COMP2
INM) a CubeMX-ben kell beállítani – a pinout nézet ezt nem mutatja. Az L433-ban egy ADC van (ADC1).
"""
import os
import re

OUT = os.path.join(os.path.dirname(__file__), '..', 'cubemx')

# (láb, jel, üzemmód vagy None, címke)
CORE = [
    ('PC13', 'GPIO_Output', None, 'STATUS_LED'),
    ('PH0-OSC_IN (PH0)', 'RCC_OSC_IN', 'HSE-External-Oscillator', None),
    ('PH1-OSC_OUT (PH1)', 'RCC_OSC_OUT', 'HSE-External-Oscillator', None),
    ('PC0', 'ADC1_IN1', 'IN1-Single-Ended', 'HW_ID'),
    ('PC1', 'ADC1_IN2', 'IN2-Single-Ended', 'VBUS_SENSE'),   # D71: a busz 5 V-ja a modulnál
    ('PB0', 'ADC1_IN15', 'IN15-Single-Ended', 'HW_REV'),
    ('PC4', 'USART3_TX', 'Asynchronous', 'UART_TX'),         # F303-on USART1, L433-on USART3
    ('PC5', 'USART3_RX', 'Asynchronous', 'UART_RX'),
    ('PA11', 'CAN1_RX', 'CAN_Activate', 'CAN_RX'),
    ('PA12', 'CAN1_TX', 'CAN_Activate', 'CAN_TX'),
    ('PA13', 'SYS_JTMS-SWDIO', 'Serial_Wire', 'SWDIO'),
    ('PA14', 'SYS_JTCK-SWCLK', 'Serial_Wire', 'SWCLK'),
]
# Az L4-es CubeMX-adatbázis minden ADC-lábat megosztott jelként vár (ADCx_INn + SH.ADCx_INn.0=ADC1_INn,<mód>), akkor is,
# ha csak egy ADC van – különben a betöltéskor eldobja a módot, és az ADC1 nem kapcsol be (fejsorból kipróbálva, 10-22).
PWM = 'PWM'   # TIM-csatorna PWM-módban (SH-bejegyzéssel)
EXTI = 'EXTI'

MODULES = {
    'led-modul': [
        ('PC2', 'ADC1_IN3', 'IN3-Single-Ended', 'V_RAIL_SENSE'),
        ('PC3', 'ADC1_IN4', 'IN4-Single-Ended', 'T_SENSE'),       # D78: MCP9701A
        ('PB1', 'ADC1_IN16', 'IN16-Single-Ended', 'VIN_SENSE'),   # D71, D78: 24 V a főbiztosíték előtt
        ('PA0', 'ADC1_IN5', 'IN5-Single-Ended', 'DS1'),
        ('PA1', 'ADC1_IN6', 'IN6-Single-Ended', 'DS2'),
        ('PA2', 'ADC1_IN7', 'IN7-Single-Ended', 'DS3'),
        ('PA7', 'ADC1_IN12', 'IN12-Single-Ended', 'DS4'),
        ('PA5', 'ADC1_IN10', 'IN10-Single-Ended', 'DS5'),
        ('PA6', 'ADC1_IN11', 'IN11-Single-Ended', 'DS6'),
        ('PA4', 'DAC1_OUT1', 'DAC_OUT1_ExtAndInt', 'DAC_THR'),   # kívül tesztpont + belül a COMP2 INM
        ('PA3', 'COMP2_INP', 'INP', 'I_SENSE'),       # + ADC1_IN8 – a CubeMX egy lábra csak egy jelet enged, a firmware mindkettőt
        ('PB12', 'GPIO_Output', None, 'DRV_EN'),      # a TIM1_BKIN / TIM15_BKIN AF-et NEM szabad bekapcsolni
        ('PA8', 'TIM1_CH1', PWM, 'CH1_PWM'),
        ('PA9', 'TIM1_CH2', PWM, 'CH2_PWM'),
        ('PA10', 'TIM1_CH3', PWM, 'CH3_PWM'),
        ('PB14', 'TIM15_CH1', PWM, 'CH4_PWM'),        # D78: a TIM8 helyett (az L433-ban nincs TIM8)
        ('PB15', 'TIM15_CH2', PWM, 'CH5_PWM'),
        ('PB8', 'TIM16_CH1', PWM, 'CH6_PWM'),
    ],
    'rele-modul': [
        ('PB12', 'GPIO_Output', None, 'REL1'),
        ('PB13', 'GPIO_Output', None, 'REL2'),
        ('PB14', 'GPIO_Output', None, 'REL3'),
        ('PB15', 'GPIO_Output', None, 'REL4'),
        ('PA0', 'ADC1_IN5', 'IN5-Single-Ended', 'CT_SENSE'),
        ('PB1', 'ADC1_IN16', 'IN16-Single-Ended', 'VIN_SENSE'),   # D71, D78: a tekercs-táp
    ],
    'bemeneti-modul': [(f'PA{i}', EXTI, None, f'IN{i}') for i in range(11)]
                      + [(f'PB{i}', EXTI, None, f'IN{i}') for i in range(11, 16)]
                      + [('PB8', 'I2C1_SCL', 'I2C', 'I2C1_SCL'),
                         ('PB9', 'I2C1_SDA', 'I2C', 'I2C1_SDA'),
                         # PC2 EXTI-ként az IN2 (PA2) EXTI2-vonalával ütközne → sima bemenet, a firmware lekérdezi
                         ('PC2', 'GPIO_Input', None, 'HDC_ALERT')],
}


def ioc(name, pins):
    L = ['#MicroXplorer Configuration settings - do not modify', 'File.Version=6', 'KeepUserPlacement=false',
         'Mcu.Family=STM32L4']
    ips = ['NVIC', 'RCC', 'SYS', 'CAN1', 'USART3']
    body = []
    exti = []
    vps = []   # virtuális lábak (belső kapcsolatok, időzítő bekapcsolása)
    for pin, sig, mode, label in pins:
        ip = None
        if sig == EXTI:
            n = int(pin[2:])
            body.append(f'{pin}.Signal=GPXTI{n}')
            exti.append(n)
        elif mode == PWM:
            tim, ch = sig.split('_')
            k = ch[2:]
            body.append(f'{pin}.Signal=S_{sig}')
            body.append(f'SH.S_{sig}.0={sig},PWM Generation{k} CH{k}')
            body.append(f'SH.S_{sig}.ConfNb=1')
            body.append(f'{tim}.Channel-PWM\\ Generation{k}\\ CH{k}=TIM_CHANNEL_{k}')
            ip = tim
        elif sig.startswith('ADC'):
            ch = sig.split('_')[1]
            body.append(f'{pin}.Signal=ADCx_{ch}')
            body.append(f'SH.ADCx_{ch}.0={sig},{mode}')
            body.append(f'SH.ADCx_{ch}.ConfNb=1')
            body.append(f'{pin}.GPIO_Mode=GPIO_MODE_ANALOG')
            ip = sig.split('_')[0]
        elif sig == 'DAC1_OUT1':
            # a PA4 a DAC1_OUT1 és a COMP-ok közös analóg csoportja
            body += [f'{pin}.Signal=COMP_DAC11_group', f'SH.COMP_DAC11_group.0={sig},{mode}', 'SH.COMP_DAC11_group.ConfNb=1']
            ip = 'DAC1'
        else:
            body.append(f'{pin}.Signal={sig}')
            if mode:
                body.append(f'{pin}.Mode={mode}')
            if sig.startswith(('I2C1', 'COMP2')):
                ip = sig.split('_')[0]
            if sig == 'COMP2_INP':
                # a COMP2 negatív bemenete belül a DAC1_OUT1 (virtuális láb)
                body += ['VP_COMP2_VS_DACOUT1.Mode=INM_DACOUT1', 'VP_COMP2_VS_DACOUT1.Signal=COMP2_VS_DACOUT1']
                vps.append('VP_COMP2_VS_DACOUT1')
        if label:
            body.append(f'{pin}.GPIO_Label={label}')
            if sig not in (EXTI,) and mode != PWM:
                body.append(f'{pin}.GPIOParameters=GPIO_Label')
        if ip and ip not in ips:
            ips.append(ip)
    for n in exti:
        body += [f'SH.GPXTI{n}.0=GPIO_EXTI{n}', f'SH.GPXTI{n}.ConfNb=1']
    tims = sorted({i for i in ips if i.startswith('TIM')})
    for t in tims:
        if t in ('TIM16', 'TIM17'):   # az egycsatornás időzítőt külön be kell kapcsolni („Activated”)
            body += [f'VP_{t}_VS_ClockSourceINT.Mode=Enable_Timer', f'VP_{t}_VS_ClockSourceINT.Signal={t}_VS_ClockSourceINT']
            vps.append(f'VP_{t}_VS_ClockSourceINT')
        chans = sorted({l.split('=')[0].split('.', 1)[1].replace('\\', '') for l in body if l.startswith(t + '.Channel')})
        body.append(f'{t}.IPParameters=' + ','.join(chans))
    pin_list = [p for p, *_ in pins] + vps + ['VP_SYS_VS_Systick']
    L += [f'Mcu.IP{i}={ip}' for i, ip in enumerate(ips)] + [f'Mcu.IPNb={len(ips)}']
    L += ['Mcu.Name=STM32L433R(B-C)Tx', 'Mcu.Package=LQFP64']
    L += [f'Mcu.Pin{i}={p}' for i, p in enumerate(pin_list)] + [f'Mcu.PinsNb={len(pin_list)}']
    L += ['Mcu.UserConstants=', 'Mcu.UserName=STM32L433RCTx',
          'NVIC.PriorityGroup=NVIC_PRIORITYGROUP_4',
          'NVIC.SysTick_IRQn=true\\:15\\:0\\:false\\:false\\:true\\:false\\:true\\:false',
          # az ADC órajele a SYSCLK-ból – nélküle a CubeMX nem generál kódot („IP not ready: Clock”)
          'RCC.ADCCLockSelection=RCC_ADCCLKSOURCE_SYSCLK', 'RCC.HSE_VALUE=8000000', 'RCC.IPParameters=ADCCLockSelection,HSE_VALUE',
          'VP_SYS_VS_Systick.Mode=SysTick', 'VP_SYS_VS_Systick.Signal=SYS_VS_Systick',
          f'ProjectManager.ProjectName={name}', 'ProjectManager.TargetToolchain=CMake',
          'ProjectManager.DeviceId=STM32L433RCTx']
    # a .ioc Java-properties: a kulcsban a szóközt escapelni kell (pl. „PH0-OSC_IN\\ (PH0).Mode”)
    body = [re.sub(r'(?<!\\) ', r'\\ ', k) + '=' + v for k, v in (x.split('=', 1) for x in body)]
    L += sorted(set(body))
    return '\n'.join(L) + '\n'


for name, extra in MODULES.items():
    pins = CORE + extra
    used = [p for p, *_ in pins]
    dup = {p for p in used if used.count(p) > 1}
    assert not dup, f'{name}: kétszer használt láb: {dup}'
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f'{name}.ioc'), 'w') as f:
        f.write(ioc(name, pins))
    print('ok', name, len(pins), 'láb')
