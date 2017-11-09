# worker for handling T0 CAEN HV unit
# Aaron Fienberg
# November 2017

import sys
from serial import Serial
from functools import partial
from worker_common import workerstartup, work
from caenHV import *


def handle_caen_mesasge(caen, handler_map, message):
    command_list = message.strip().split()
    if command_list[0] in handler_map:
        try:
            return handler_map[command_list[0]](serial_port, *command_list[1:])
        except (TypeError, ValueError):
            return 'invalid caen command'
    else:
        return 'unrecognized caen command'


def main():
    caen = None
    try:
        open_caen_port('/dev/caenHV')
    except:
        pass

    workerstartup('caenHV')
    if caen is not None:
        handler_map = {}
        handler_map['setpt'] = read_voltage
        work('caenHV', partial(handle_caen_mesasge, caen, handler_map))
    else:
        work('caenHV', lambda x: 'caenHV module is not connected')


if __name__ == '__main__':
    main()
