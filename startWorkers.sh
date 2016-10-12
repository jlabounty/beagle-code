#!/bin/bash
pushd /home/g-2/beagle-code
masteripstr=`ifconfig eth0 | grep 192.168.1.21`
[[ ! -z $masteripstr ]] && ./startMasterWorkers.sh || ./startSlaveWorkers.sh
popd
exit 0
