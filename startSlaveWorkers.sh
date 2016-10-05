#!/bin/bash

python spiworker.py 1 &
python spiworker.py 2 &
python filterworker.py 1 &
exit 0