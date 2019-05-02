#!/bin/sh
cd /home/pi/myhome/ticker
sudo python ticker.py > ticker.log 2> ticker.err
cd / 
