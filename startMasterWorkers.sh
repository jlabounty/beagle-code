#!/bin/bash

python spiworker.py 1 &
python spiworker.py 2 &
python bkworker.py 1 &
python bkworker.py 2 &
python bkworker.py 3 &
python bkworker.py 4 &
python jmuworker.py  &
exit 0