from caenHV import *
import sys

def main():
    if len(sys.argv) != 2:
        print 'Usage: read_voltage [chanNum]'
        sys.exit(0)
    chan = int(sys.argv[1])
    caen = open_caen_port('/dev/caenHV')
    print('Reading back voltage for channel {}: '.format(chan))
    print(read_voltage(caen,chan))


if __name__ == '__main__':
    main()