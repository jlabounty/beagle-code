#!/bin/bash
#
start() {
    pushd /home/g-2/beagle-code
    ./beagle_broker &
    popd
}

ps auxw | grep beagle_broker | grep -v grep && echo already running! || start
exit 0
