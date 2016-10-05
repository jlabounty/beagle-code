#!/bin/bash
ifconfig eth0 | grep 192.168.1.21 && ./startMasterWorkers.sh || ./startSlaveWorkers.sh
exit 0
