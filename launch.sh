#!/bin/sh

python hosts/smartMeter.py 1 127.0.0.1
python hosts/concentrator.py &
python hosts/mainServer.py &