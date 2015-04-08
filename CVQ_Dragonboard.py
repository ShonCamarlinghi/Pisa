#!/usr/bin/python/2.7

import time 
import threading
import sys
import os
import os.path
import string
import re

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
adb = os.popen('adb devices').read().strip().split('\n')[1:]
deviceID = adb[0].split('\t')[0]
device = MonkeyRunner.waitForConnection(1000, deviceID) 
total_n = 200.0
total_t = 455*10
case = ['Clean']
KW = 'NihaoZhongXin'
outDir = '/home/ate/workspace/es804_CVQ_QS/CVQ'
fname = os.path.join(outDir, KW + '_CVQ.txt')
f = open(fname, 'w')


def adbConnection():
    try:
        device = MonkeyRunner.waitForConnection(5, deviceID)
        print 'Connected to device: %s' % deviceID
    except IndexError:
        print 'Could not get adb connection at %s' % time.asctime()
        sys.exit(1)
 
def asr(ASRres, b):
    print "ASR"    
    while True:
        logcat1 = device.shell('logcat -d -v time')
        m1 = re.search(r'parsed response', logcat1)
        if m1:
            print 'got ASR response', m1.group()
            a = re.split(r'parsed response(.*)', (logcat1))
            a = string.upper(a[len(a)-2])
           # a = rstrip('\r')
            ASRres.append(a.rstrip('\r') + b)
            print ASRres
            break
        else:
            print "Waiting for ASR response..."
            time.sleep(1)   
 
def snooz():
    
    device.shell('am force-stop com.android.browser')
    device.touch(460, 900, MonkeyDevice.DOWN_AND_UP)
    #device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)
    time.sleep(1)
    device.shell('logcat -c')
    device.touch(260, 805, MonkeyDevice.DOWN_AND_UP)
    while True:
	logcat2 = device.shell('logcat -d -v time')
	m2 = re.search(r'Time taken for: setting cvs preset', logcat2)
	if m2:
		print "CVQ preset set"
		break
        else:
		time.sleep(1)
     

def frr(value, n, start_t):
    z =  (total_n-n)/total_n*100            
    f.write("\nNoise: %s, KW detect count: %d, FRR rate: %.2f" % (value, n, round(z,2)))
    f.write("\nStart time: %s" % (start_t))
    f.write("\nEnd time: %s \n" % (time.asctime()))
    f.write("==================================================\n\n")
     

def far(value, n, start_t):
    f.write("Noise: %s, KW detect count: %d" % (value, n))
    f.write("\nStart time: %s" % (start_t))
    f.write("\nEnd time: %s \n" % (time.asctime()))
    f.write("==================================================\n\n")
 

def asrCase(value, ASRres):  
 
    for i in ASRres:
        f.write(''.join(str(i))) 
        f.write('\n')
                
         
def KWcount(value): 
    n = 0
    start_t = time.asctime()
    start = time.time()
    ASRres =[]
    print "\nStart time: %s, case: %s" % (start_t, value)
    device.touch(260, 805, MonkeyDevice.DOWN_AND_UP)
    while True:
        logcat0 = device.shell('logcat -d -v time')
        try: 
            if 'detected cvs event' in logcat0: 
                n += 1
                delta_t = time.time() - start
                print "KW detection: %d, Lapsed time: %d" % (n, delta_t)
                b = ' (Utterance_%(n)03d)' % {"n":n}
                asr(ASRres, b)
                snooz()
            else:
                #print n
                delta_t = time.time() - start    
                if int(delta_t) >= total_t:
                    break
	except TypeError:
	        asrCase(value, ASRres)
                adbConnection()
    asrCase(value, ASRres)
    #frr(value,n, start_t)


print 'Hello! :), device under test s/n: %s' % deviceID
 

for value in case:
    KWcount(value)
f.close()
