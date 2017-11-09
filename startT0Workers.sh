#!/bin/bash
pushd /home/g-2/beagle-code

python spiworker.py 1 &
python spiworker.py 2 &
python bkworker.py 1 &
python caenHVworker.py &

exit 0
