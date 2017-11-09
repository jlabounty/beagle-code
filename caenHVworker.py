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
            return handler_map[command_list[0]](caen, *command_list[1:])
        except (TypeError, ValueError):
            return 'invalid caen command'
    else:
        return 'unrecognized caen command'


def main():
    caen = None
    try:
        caen = open_caen_port('/dev/caenHV')
    except:
        pass

    workerstartup('caenHVworkerproc')
    if caen is not None:
        handler_map = {}
        handler_map['readvolt'] = read_voltage
        handler_map['readcurr'] = read_current
        handler_map['setvolt'] = set_voltage
        handler_map['getid'] = get_id
        handler_map['turnon'] = turn_on
        handler_map['turnoff'] = turn_on
        handler_map['stat'] read_status
        work('caenHV', partial(handle_caen_mesasge, caen, handler_map))
    else:
        work('caenHV', lambda x: 'caenHV module is not connected')


if __name__ == '__main__':
    main()
