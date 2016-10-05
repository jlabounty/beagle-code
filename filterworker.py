# Worker for handling control of a thor labs filter wheel
# Aaron Fienberg
# October 2016

from worker_common import workerstartup, work

def process_message_filter(message):
	# does nothing for now
	return message + ': from filterworker'

def main():
	# logic to check if serial port can be opened goes here
	# 

	workerstartup('filterwheelworker')
	work('filter', process_message_filter)
	
if __name__ == "__main__":
    main()