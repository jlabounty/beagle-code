#!/bin/bash
ifconfig en0 | grep 131.225.*.160 && ./startMasterWorkers.sh || ./startSlaveWorkers.sh
exit 0