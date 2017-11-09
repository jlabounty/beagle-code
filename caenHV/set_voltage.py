from caenHV import *
import sys

def main():
    if len(sys.argv) != 3:
        print 'Usage: set_voltage [chanNum] [voltage]'
        sys.exit(0)
    chan, voltage = int(sys.argv[1]), float(sys.argv[2])
    caen = open_caen_port('/dev/caenHV')
    print(set_voltage(caen, chan, voltage))
    print('set voltage. Reading back voltage for channel {}: '.format(chan))
    print(read_voltage(caen,chan))


if __name__ == '__main__':
    main()