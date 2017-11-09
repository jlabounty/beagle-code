import re
import serial

val_reg = re.compile('BD:00,CMD:OK,VAL:([\\w .]+)')

def open_caen_port(path):
    return serial.Serial(path, 9600, timeout=1, xonxoff=True)

def read_response(caen):
    response = ''
    while len(response) == 0 or response[-1] != '\n':
        new_char = caen.read(1)
        if new_char == '':
            return 'failed serial read'
        else:
            response += new_char    
    return response[:-2]

def get_id(caen):
    caen.write('$BD:00,CMD:MON,PAR:BDNAME\r\n')
    return read_response(caen)

def read_voltage(caen, chan_num):
    caen.write('$BD:00,CMD:MON,CH:{},PAR:VSET\r\n'.format(chan_num))
    resp = read_response(caen)
    search = val_reg.search(resp)
    if search:
        return search.groups()[0]
    else:
        return 'fail'


def turn_on(caen, chan_num):
    caen.write('$BD:00,CMD:SET,CH:{},PAR:ON\r\n'.format(chan_num))
    return read_response(caen)


def turn_off(caen, chan_num):
    caen.write('$BD:00,CMD:SET,CH:{},PAR:OFF\r\n'.format(chan_num))
    return read_response(caen)


def read_status(caen, chan_num):
    caen.write('$BD:00,CMD:MON,CH:{},PAR:STAT\r\n'.format(chan_num))
    return read_response(caen)


def set_voltage(caen, chan_num, voltage):
    caen.write('$BD:00,CMD:SET,CH:{0},PAR:VSET,VAL:{1:.1f}\r\n'.format(chan_num, voltage))
    return(read_response(caen))