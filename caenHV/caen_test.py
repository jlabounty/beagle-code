from serial import Serial
from caenHV import *

caen = open_caen_port('/dev/caenHV')
print(get_id(caen))
for ch in range(0,4):
    print(read_voltage(caen, ch))

print('setting channel 2 voltage to 50')
set_voltage(caen, 2, 50)
for ch in range(0,4):
    print(read_voltage(caen, ch))

print('setting channel voltages to 0')
for ch in range(0,4):
    set_voltage(caen, ch, 0)

for ch in range(0,4):
    print(read_voltage(caen, ch))

