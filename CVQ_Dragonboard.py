#!/usr/bin/python/2.7
import time
import threading
import sys
import os
import os.path
import string
import re
import subprocess
import signal
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

#os.system('adb root')
#time.sleep(2)
#os.system('adb remount')
#time.sleep(2)
adb = os.popen('adb devices').read().strip().split('\n')[1:]
deviceID = adb[0].split('\t')[0]
device = MonkeyRunner.waitForConnection(1000, deviceID)
print 'Hello! :), device under test s/n: %s' % deviceID
device.shell('logcat -c')
total_n = 20.0   # number of KWs per case
total_t = 620  # length in seconds per case
case = ['Babble6']  # test cases
outDir = '/home/ate/workspace/es804_CVQ_QS/English/CVQ'
FW = '51747'
VP = 'VPon'
Delay = '50ms'
# Uncomment below 3 lines for FRR/FA test
#KW = 'NihaoZhongXin'
#fname = os.path.join(outDir, KW + '_CVQ.txt')
#f = open(fname, 'w')

def adbConnection():
    try:
        device = MonkeyRunner.waitForConnection(5, deviceID)
        print 'Connected to device: %s' % deviceID
    except IndexError:
        print 'Could not get adb connection at %s, is your device off/rebooting?' % time.asctime()
        sys.exit(1)

def exitGracefully(signum, frame):
	print 'Exiting Gracefully...'
	signal.signal(signal.SIGINT, signal.getsignal(signal.SIGINT))
	device.shell('am force-close com.android.commands.monkey')
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

def pull_flac(outDir, value, flacFolder, n):
	print "Starting pull"
	#command = ["bash", "./flac.sh", outDir, flac_name, b]
	#subprocess.call(command, shell=False)
	os.system(['mkdir', '%s/%s' % (outDir, flacFolder)])
	flacPath='%s/%s/flac/%s.flac' % (outDir, flacFolder, n)
	print flacPath
	combPath='%s/%s/comb/%scomb.pcm' % (outDir, flacFolder, n)
	print combPath
	os.system('adb pull /data/data/com.audience.voiceqmultikeyword/files/flacdumpapp.flac %s' % flacPath )
	os.system('adb pull /data/data/com.audience.voiceqmultikeyword/files/combineddumpapp %s' % combPath )
	print "Ended pull to %s" % outDir

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
	fname = os.path.join(outDir, value + '_' + Delay + '_B'+ FW + VP +'_CVQ.txt')
	f = open(fname, 'w')
	for i in ASRres:
		f.write(''.join(str(i)))
		f.write('\n')
	f.close()
def test(outDir, flac_name, b):
	print "Start"
	command=["sh", "./test.sh", outDir, flac_name, b ]
	subprocess.call(command, shell=False)
	print "End"
	#subprocess.check_output("echo", "Hello World!")

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
				flacFolder = '%s_%s_%s_%s' % (Delay, value, FW, VP)
				#os.system('adb root')
                #os.system('adb wait-for-device')
				pull_flac(outDir, value, flacFolder, n)
				#comment out above 3 lines for FRR/FA test
				#test(outDir, flac_name, b)
				snooz()
			else:
				delta_t = time.time() - start
				if int(delta_t) >= total_t:
					break
		except TypeError:
			asrCase(value, ASRres)
			adbConnection()
	asrCase(value, ASRres)
	#frr(value,n, start_t)
	#far(value, n, start_t)

def main():
	for value in case:
		KWcount(value)
	#f.close()
    # Uncomment above line for FRR/FA test

if __name__ == '__main__':
	signal.signal(signal.SIGINT, exitGracefully)
	main()

