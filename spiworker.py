# Worker for handling control of a single spi interface
# Aaron Fienberg
# October 2016

import sys
from sipmspi import SipmSPI
from functools import partial
from worker_common import workerstartup, work

PINS = [{'sipmpins': [11, 12, 13, 14], 'chippins': [15, 16]}, {'sipmpins': [23, 24, 25, 26], 'chippins': [41, 42]}]

sipmspi = None

def sipm_control(sipmspi, message):
    command_list = message.strip().split()
    if command_list[0] == 'chan':
        command_list = command_list[1:]
    else:
        return 'ERROR: invalid spi command'
    # get sipm number
    sipm_num = None
    try:
        sipm_num = int(command_list[0])
    except (ValueError, IndexError):
        pass
    finally:
        if sipm_num not in range(16):
            return 'ERROR: invalid sipm number'

    sipmspi.select_sipm(sipm_num)
    
    #get chip 
    chip = None
    try:
        chip = command_list[1]
    except IndexError:
        pass
    finally:
        if chip not in ['gain', 'temp', 'mem']:
            return 'ERROR: invalid chip selection'

    if chip == 'temp':
        sipmspi.chip_select('temp')
        return sipmspi.read_temperature()

    elif chip == 'mem':
        sipmspi.chip_select('mem')
        memstr = sipmspi.read_eeprom_page(1)
        return memstr if memstr is not None else ''

    elif chip == 'gain':
        sipmspi.chip_select('pga')
        new_gain = None
        try:
            new_gain = int(command_list[2])
        except IndexError:
            return sipmspi.read_gain()
        except ValueError:
            pass
        
        if 0 <= new_gain <= 80:
            return sipmspi.set_gain(new_gain)
        else:
            return 'ERROR: invalid gain setting'

    else:
        return 'ERROR: invalid board command'

# def process_message_spi(message):
#     # does nothing for now
#     return message + ': from spiworker'

def main():
    if len(sys.argv) != 2:      
        print 'Usage: spiworker [spinum]'
    spinum = None
    try:
        spinum = int(sys.argv[1])
    except ValueError:
        spinum = -1
    finally:
        if spinum not in [1, 2]:
            print 'error! [spinum] must be 1 or 2!'
            sys.exit(0)
    workerstartup('spiworker%i' % spinum)
    sipmspi = SipmSPI(spinum, **PINS[spinum - 1])
    work('spi%i' % spinum, partial(sipm_control, sipmspi))
    
if __name__ == '__main__':
    main()
