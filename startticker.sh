#!/bin/sh
cd /home/pi/myhome
sudo python ticker.py > ticker.log 2> ticker.err
cd / 
