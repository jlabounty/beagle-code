#!/bin/bash
masteripstr=`ifconfig eth0 | grep 192.168.1.21`
[[ ! -z $masteripstr ]] && ./startMasterWorkers.sh || ./startSlaveWorkers.sh
exit 0
