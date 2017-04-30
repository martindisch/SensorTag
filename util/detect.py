#!/usr/bin/python

"""Detects consecutive same humidity values in a history CSV file.

Having more than about 90 of those in a row seems to be a
good indication of low battery on the SensorTag.

Use as ./detect.py filename.csv
"""

import sys

same = 90

if len(sys.argv) < 2:
    print "Missing argument: filename"
    sys.exit(1)
    
hum = -1
count = 0
startline = ""
with open(sys.argv[1], 'r') as f:
    line = f.readline().strip('\n')
    while line:
        current = float(line.split(",")[2])
        if current == hum and current < 97:
            count += 1
        else:
            # process previous
            if count >= same:
                print "%d entries starting from %s" % (count, startline)
            # reset
            startline = line
            hum = current
            count = 0
        
        line = f.readline().strip('\n')
