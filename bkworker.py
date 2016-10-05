# Worker for handling control of a single bk power supply
# Aaron Fienberg
# October 2016

import sys
from worker_common import workerstartup, work

def process_message_bk(message):
	# does nothing for now
	return message + ': from bkworker'

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
	# 

	workerstartup('bkworker%i' % bknum)
	work('bk%i' % bknum, process_message_bk)
	
if __name__ == "__main__":
    main()