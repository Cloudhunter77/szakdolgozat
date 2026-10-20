"""STM32CubeMX-projektek (.ioc) a három modulhoz – a MODULMAG-SPEC 7. fejezetének lábkiosztásából.

Használat: python3 hardware/gen/cubemx.py  →  hardware/cubemx/<modul>/<modul>.ioc
A CubeMX-ben megnyitva a lábak a jelükkel és a címkéjükkel jelennek meg; ha egy jel nem rendelhető a lábhoz, vagy két
funkció ütközik, a CubeMX jelzi. A jel- és üzemmódnevek a CubeMX 6.18 adatbázisából (STM32F303R(D-E)Tx.xml, IP/*.xml)
és a NUCLEO-F303RE board-projektből valók. A DAC/COMP/ADC-belső kapcsolatokat (COMP2 → TIM1/TIM8 BKIN2, DAC1 → COMP2
INM) a CubeMX-ben kell beállítani – a pinout nézet ezt nem mutatja.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'cubemx')

# (láb, jel, üzemmód vagy None, címke)
CORE = [
    ('PC13', 'GPIO_Output', None, 'STATUS_LED'),
    ('PF0-OSC_IN', 'RCC_OSC_IN', 'HSE-External-Oscillator', None),
    ('PF1-OSC_OUT', 'RCC_OSC_OUT', 'HSE-External-Oscillator', None),
    ('PC0', 'ADC1_IN6', 'IN6-Single-Ended', 'HW_ID'),
    ('PC1', 'ADC1_IN7', 'IN7-Single-Ended', 'VIN_SENSE'),
    ('PB0', 'ADC3_IN12', 'IN12-Single-Ended', 'HW_REV'),
    ('PC4', 'USART1_TX', 'Asynchronous', 'UART_TX'),
    ('PC5', 'USART1_RX', 'Asynchronous', 'UART_RX'),
    ('PA11', 'CAN_RX', 'CAN_Activate', 'CAN_RX'),
    ('PA12', 'CAN_TX', 'CAN_Activate', 'CAN_TX'),
    ('PA13', 'SYS_JTMS-SWDIO', 'Serial_Wire', 'SWDIO'),
    ('PA14', 'SYS_JTCK-SWCLK', 'Serial_Wire', 'SWCLK'),
]
# lábak, ahol ugyanaz az ADC-csatorna az ADC1-en és az ADC2-n is elérhető (CubeMX-adatbázis)
ADC12_SHARED = {'PC0', 'PC1', 'PC2', 'PC3', 'PB11'}
PWM = 'PWM'   # TIM-csatorna PWM-módban (SH-bejegyzéssel)
EXTI = 'EXTI'

MODULES = {
    'led-modul': [
        ('PC2', 'ADC1_IN8', 'IN8-Single-Ended', 'V_RAIL_SENSE'),
        ('PC3', 'ADC1_IN9', 'IN9-Single-Ended', 'NTC'),
        ('PA0', 'ADC1_IN1', 'IN1-Single-Ended', 'DS1'),
        ('PA1', 'ADC1_IN2', 'IN2-Single-Ended', 'DS2'),
        ('PA2', 'ADC1_IN3', 'IN3-Single-Ended', 'DS3'),
        ('PA3', 'ADC1_IN4', 'IN4-Single-Ended', 'DS4'),
        ('PA5', 'ADC2_IN2', 'IN2-Single-Ended', 'DS5'),
        ('PA6', 'ADC2_IN3', 'IN3-Single-Ended', 'DS6'),
        ('PA4', 'DAC1_OUT1', None, 'DAC_THR'),        # → COMP2 INM (belül)
        ('PA7', 'COMP2_INP', None, 'I_SENSE'),        # + ADC2_IN4 (a CubeMX-ben megosztott analóg jelként)
        ('PB12', 'GPIO_Output', None, 'DRV_EN'),      # a TIM1_BKIN AF-et NEM szabad bekapcsolni
        ('PA8', 'TIM1_CH1', PWM, 'CH1_PWM'),
        ('PA9', 'TIM1_CH2', PWM, 'CH2_PWM'),
        ('PA10', 'TIM1_CH3', PWM, 'CH3_PWM'),
        ('PC6', 'TIM8_CH1', PWM, 'CH4_PWM'),
        ('PC7', 'TIM8_CH2', PWM, 'CH5_PWM'),
        ('PC8', 'TIM8_CH3', PWM, 'CH6_PWM'),
    ],
    'rele-modul': [
        ('PB12', 'GPIO_Output', None, 'REL1'),
        ('PB13', 'GPIO_Output', None, 'REL2'),
        ('PB14', 'GPIO_Output', None, 'REL3'),
        ('PB15', 'GPIO_Output', None, 'REL4'),
        ('PA0', 'ADC1_IN1', 'IN1-Single-Ended', 'CT_SENSE'),
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
         'Mcu.Family=STM32F3']
    ips = ['NVIC', 'RCC', 'SYS', 'CAN', 'USART1']
    body = []
    exti = []
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
        elif pin in ADC12_SHARED and sig.startswith('ADC'):
            # a csatorna az ADC1-en és az ADC2-n is megvan → a CubeMX megosztott jelként várja (ADCx_INn + SH)
            ch = sig.split('_')[1]
            body.append(f'{pin}.Signal=ADCx_{ch}')
            body.append(f'SH.ADCx_{ch}.0={sig},{mode}')
            body.append(f'SH.ADCx_{ch}.ConfNb=1')
            body.append(f'{pin}.GPIO_Mode=GPIO_MODE_ANALOG')
            ip = sig.split('_')[0]
        else:
            body.append(f'{pin}.Signal={sig}')
            if mode:
                body.append(f'{pin}.Mode={mode}')
            if sig.startswith('ADC'):
                ip = sig.split('_')[0]
                body.append(f'{pin}.GPIO_Mode=GPIO_MODE_ANALOG')
            elif sig.startswith(('I2C1', 'DAC1', 'COMP2')):
                ip = sig.split('_')[0]
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
        chans = sorted({l.split('=')[0].split('.', 1)[1].replace('\\', '') for l in body if l.startswith(t + '.Channel')})
        body.append(f'{t}.IPParameters=' + ','.join(chans))
    pin_list = [p for p, *_ in pins] + ['VP_SYS_VS_Systick']
    L += [f'Mcu.IP{i}={ip}' for i, ip in enumerate(ips)] + [f'Mcu.IPNb={len(ips)}']
    L += ['Mcu.Name=STM32F303R(D-E)Tx', 'Mcu.Package=LQFP64']
    L += [f'Mcu.Pin{i}={p}' for i, p in enumerate(pin_list)] + [f'Mcu.PinsNb={len(pin_list)}']
    L += ['Mcu.UserConstants=', 'Mcu.UserName=STM32F303RETx',
          'NVIC.PriorityGroup=NVIC_PRIORITYGROUP_4',
          'NVIC.SysTick_IRQn=true\\:15\\:0\\:false\\:false\\:true\\:false\\:true\\:false',
          'RCC.HSE_VALUE=8000000', 'RCC.IPParameters=HSE_VALUE',
          'VP_SYS_VS_Systick.Mode=SysTick', 'VP_SYS_VS_Systick.Signal=SYS_VS_Systick',
          f'ProjectManager.ProjectName={name}', 'ProjectManager.TargetToolchain=CMake',
          'ProjectManager.DeviceId=STM32F303RETx']
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
