#!/usr/bin/env python3
"""Nem-interaktív soros log olvasó (Claude Code-hoz, ahol az `idf.py monitor` nem fut TTY nélkül).

Használat:
  python serial_log.py /dev/ttyACM0 30            # 30 mp log
  python serial_log.py /dev/ttyACM0 30 --reset    # reset után a teljes boot log (QR kód is benne van)
  python serial_log.py /dev/ttyACM0 5 --cmd "matter onboardingcodes ble"   # parancs a chip shellnek
"""
import sys
import time

import serial

args = [a for a in sys.argv[1:]]
port = args[0] if args and not args[0].startswith("--") else "/dev/ttyACM0"
secs = float(args[1]) if len(args) > 1 and not args[1].startswith("--") else 20.0
reset = "--reset" in args
cmd = args[args.index("--cmd") + 1] if "--cmd" in args else None

s = serial.Serial()
s.port, s.baudrate, s.timeout = port, 115200, 0.2
s.dtr = False  # ne húzza le a BOOT/strapping lábat
s.rts = False  # ne tartsa resetben
s.open()

if reset:
    s.rts = True
    time.sleep(0.1)
    s.rts = False
if cmd:
    time.sleep(0.3)
    s.write((cmd + "\n").encode())

end = time.time() + secs
try:
    while time.time() < end:
        line = s.readline()
        if line:
            sys.stdout.write(line.decode(errors="replace"))
            sys.stdout.flush()
except KeyboardInterrupt:
    pass
finally:
    s.close()
