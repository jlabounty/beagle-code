#!/bin/bash
pushd /home/g-2/beagle-code
masteripstr=`ifconfig eth0 | grep '192.168.\{2,4\}.21'`
[[ ! -z $masteripstr ]] && ./startMasterWorkers.sh || ./startSlaveWorkers.sh
popd
exit 0
