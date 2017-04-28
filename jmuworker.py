# Worker for handling control of jmu power supply
# Aaron Fienberg
# April 2017

from worker_common import workerstartup, work
import Adafruit_BBIO.GPIO as GPIO


def process_message_jmu(message):
    command = None
    try:
        command = message.strip().split()[0]
    except:
        return 'invalid message'
    if message == 'on':
        GPIO.output("P8_10", GPIO.HIGH)
        return 'turned on'
    elif message == 'off':
        GPIO.output("P8_10", GPIO.LOW)
        return 'turned off'
    else:
        return 'invalid message'


def main():
    workerstartup('jmupowersupplyworker')
    GPIO.setup("P8_10", GPIO.OUT)
    GPIO.output("P8_10", GPIO.HIGH)
    work('jmu', process_message_jmu)
	
    
if __name__ == "__main__":
    main()
