import zmq
import sys

def main():
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.setsockopt(zmq.LINGER, 0)
	socket.setsockopt(zmq.RCVTIMEO, 10)
	socket.connect("tcp://localhost:6669")	
	print "sending message!"
	mstr = ''.join('%s ' % arg for arg in sys.argv[1:]).strip()
	print mstr
	socket.send(mstr)
	print "waiting for reply..."
	try:
		print "got reply " + socket.recv()
	except zmq.error.Again:
		print "timeout"


if __name__ == "__main__":
	main()