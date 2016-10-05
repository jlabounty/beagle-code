# common code for beaglebone workers
# Aaron Fienberg
# October 2016

import subprocess
import setproctitle
import sys
import zmq

def assert_not_running(proctitle):
	ps = subprocess.Popen('ps auxw'.split(), stdout=subprocess.PIPE)
	processes = ps.communicate()[0]
	if proctitle in processes:
		print "%s already running" % proctitle
		sys.exit(0)

def workerstartup(proctitle):
	assert_not_running(proctitle)
	setproctitle.setproctitle(proctitle)

def work(name, process_message):
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("ipc://%s.ipc" % name);
	while True:
		print "%s waiting for message..." % name
		message = socket.recv()
		print "received work request %s" % message
		print "sending back..." 
		socket.send(process_message(message))
