# Worker for handling control of a single bk power supply
# Aaron Fienberg
# October 2016

import sys
from serial import Serial
from functools import partial
from worker_common import workerstartup, work

def read_response(serial_port):
    response = ''
    while len(response) == 0 or response[-1] != '\n':
        new_char = serial_port.read(1)
        if new_char == '':
            return 'failed serial read'
        else:
            response += new_char
    return response[:-1]

def bk_read(serial_port, bk_command):
    serial_port.write(bk_command)
    return read_response(serial_port)

def bk_write(serial_port, write_command, read_command):
    serial_port.write(write_command)
    return bk_read(serial_port, read_command)

def read_serial(serial_port):
    return bk_read(serial_port, '*IDN?\n')

def read_output_stat(serial_port): 
    return bk_read(serial_port, 'OUTP:STAT?\n')

def read_voltage_setpt(serial_port):
    return bk_read(serial_port, 'SOUR:VOLT?\n')

def read_current_limit(serial_port):
    return bk_read(serial_port, 'SOUR:CURR?\n')

def measure_voltage(serial_port):
    return bk_read(serial_port, 'MEAS:VOLT?\n')

def measure_current(serial_port):
    return bk_read(serial_port, 'MEAS:CURR?\n')

def power_on(serial_port):
    return bk_write(serial_port, 'OUTP:STAT 1\n', 'OUTP:STAT?\n')

def power_off(serial_port):
    return bk_write(serial_port, 'OUTP:STAT 0\n', 'OUTP:STAT?\n')

def set_voltage(serial_port, voltage):
    return bk_write(serial_port, 'SOUR:VOLT %.3f\n' % voltage, 'SOUR:VOLT?\n')

def set_current_limit(serial_port, currlim):
    # do we need bounds checking?
    return bk_write(serial_port, 'SOUR:CURR %.5f\n' % currlim, 'SOUR:CURR?\n')

def read_handler(serial_port, read_command):
    if read_command == 'voltage':
        return read_voltage_setpt(serial_port)
    elif read_command == 'current':
        return read_current_limit(serial_port)
    elif read_command == 'serialno':
        return read_serial(serial_port)
    elif read_command == 'output':
        return read_output_stat(serial_port)
    else:
        return 'unrecognized bk read'

def set_handler(serial_port, set_command, value):
    fvalue = None
    try:
        fvalue = float(value)
    except ValueError:
        return 'invalid bk parameter'
    if set_command == 'voltage':
        return set_voltage(serial_port, fvalue)
    elif set_command == 'current':
        return set_current_limit(serial_port, fvalue)
    else:
        return 'unrecognized bk set'

def measure_handler(serial_port, measure_command):
    if measure_command == 'voltage':
        return measure_voltage(serial_port)
    elif measure_command == 'current':
        return measure_current(serial_port)
    else:
        return 'unrecognized bk measure'

def power_handler(serial_port, power_command):
    if power_command == 'on':
        return power_on(serial_port)
    elif power_command == 'off':
        return power_off(serial_port)
    else:
        return 'unrecognized bk command'

def handle_bk_message(serial_port, handler_map, message):
    command_list = message.strip().split()
    if command_list[0] in handler_map:
        try:
            return handler_map[command_list[0]](serial_port, *command_list[1:])
        except (TypeError, ValueError):
            return 'invalid bk command'
    else:
        return 'unrecognized bk command'

def main():
    if len(sys.argv) != 2:      
        print "Usage: bkworker [bknum]"
    bknum = None
    try:
        bknum = int(sys.argv[1])
    except ValueError:
        bknum = -1
    finally:
        if bknum not in range(1,5):
            print "error! [bknum] must be 1, 2, 3, or 4!"
            sys.exit(0)
    # logic to check if serial port can be opened goes here
    bk_serial = None
    try:
        bk_serial = Serial('/dev/bk%i' % bknum, 4800, timeout=0.5)
    except:
        bk_serial = None

    workerstartup('bkworker%i' % bknum)
    if bk_serial is not None:
        handler_map = {}
        handler_map['read'] = read_handler
        handler_map['set'] = set_handler
        handler_map['measure'] = measure_handler
        handler_map['power'] = power_handler
        work('bk%i' % bknum, partial(handle_bk_message, bk_serial, handler_map))
    else:
        work('bk%i' % bknum, lambda x: 'bk %i is not connected' % bknum)
    
if __name__ == "__main__":
    main()
