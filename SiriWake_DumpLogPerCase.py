#!/usr/bin/python/2.7
import time
import sys
import os
import os.path
import re
import signal
import pickle

total_n = 4.0
total_t = 60
case = ['Clean']  # , 'Car0', 'Pub0']
FW = 'Apple'  # test FW
KW = 'Siri'  # test KW
outDir = '/Users/scamarlinghi/workspace/Siri_WakeupTest'


def dump(data, f):
    pickle.dump(data, f, unicode)


def logCase(value):
    global FW
    global KW
    global outDir
    start_t = time.asctime()
    start = time.time()
    fname = os.path.join(outDir, KW + '_' + KW + value + '.txt')
    f = open(fname, 'a')
    f.write("\nNoise: %s,     Start time: %s" % (value, start_t))
    print "\nNoise: %s,     Start time: %s" % (value, start_t)
    data = []
    while True:
        log = os.system('idevicesyslog -d')
        try:
            m = re.search('Initialized Siri', log)
            if m:
                a = m.group()
                data.append(a)
                print data
            else:
                delta_t = time.time() - start
                if int(delta_t) >= total_t:
                    break
        except TypeError:
            dump(data, f)
            f.write("Connection lost at %s" % time.asctime())
            print "Connection lost at %s" % time.asctime()
            f.close()
    dump(data, f)
    f.write("\nNoise: %s,     End time: %s" % (value, time.asctime()))
    print "\nNoise: %s,     End time: %s" % (value, time.asctime())
    f.close()


def main():
    for value in case:
        logCase(value)


if __name__ == '__main__':
    main()

