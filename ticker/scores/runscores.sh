#!/bin/sh


cd /home/pi/myhome/ticker/scores

python scores.py -l MLB > MLB.dat
python scores.py -l NFL > NFL.dat
python scores.py -l NBA > NBA.dat
python scores.py -l NHL > NHL.dat

