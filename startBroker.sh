#!/bin/bash
#
start() {
	./beagle_broker &
}

ps auxw | grep beagle_broker | grep -v grep && echo already running! || start
exit 0