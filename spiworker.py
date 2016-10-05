# Worker for handling control of a single spi interface
# Aaron Fienberg
# October 2016

import sys
from worker_common import workerstartup, work

def process_message_spi(message):
	# does nothing for now
	return message + ': from spiworker'

def main():
	if len(sys.argv) != 2:		
		print "Usage: spiworker [spinum]"
	spinum = None
	try:
		spinum = int(sys.argv[1])
	except ValueError:
		spinum = -1
	finally:
		if spinum not in [1, 2]:
			print "error! [spinum] must be 1 or 2!"
			sys.exit(0)
	workerstartup('spiworker%i' % spinum)
	work('spi%i' % spinum, process_message_spi)
	
if __name__ == "__main__":
    main()