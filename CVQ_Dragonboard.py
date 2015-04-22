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



total_n = 20.0   # number of KWs per case
total_t = 660  # length in seconds per case
case = ['Babble6']  # test cases
outDir = '/home/ate/workspace/es804_CVQ_QS/English/CVQ'
FW = '51747'
VP = 'VPon'
Delay = '3200ms'
# Uncomment below 3 lines for FRR/FA test
#KW = 'NihaoZhongXin'
#fname = os.path.join(outDir, KW + '_CVQ.txt')
#f = open(fname, 'w')


os.system('adb root')
time.sleep(2)
os.system('adb remount')
time.sleep(2)
adb = os.popen('adb devices').read().strip().split('\n')[1:]
deviceID = adb[0].split('\t')[0]
device = MonkeyRunner.waitForConnection(1000, deviceID)
strProperty = device.getProperty('fingerprint')
print 'Build: %s' % strProperty
print 'Connected to device s/n: %s' % deviceID


d = {
	'Utterance_001':'Utterance_019',
	'Utterance_002':'Utterance_034',
	'Utterance_003':'Utterance_039',
	'Utterance_004':'Utterance_041',
	'Utterance_005':'Utterance_046',
	'Utterance_006':'Utterance_059',
	'Utterance_007':'Utterance_079',
	'Utterance_008':'Utterance_083',
	'Utterance_009':'Utterance_085',
	'Utterance_010':'Utterance_101',
	'Utterance_011':'Utterance_106',
	'Utterance_012':'Utterance_130',
	'Utterance_013':'Utterance_140',
	'Utterance_014':'Utterance_150',
	'Utterance_015':'Utterance_154',
	'Utterance_016':'Utterance_164',
	'Utterance_017':'Utterance_185',
	'Utterance_018':'Utterance_187',
	'Utterance_019':'Utterance_195',
	'Utterance_020':'Utterance_199'
}

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
	sys.exit(1)

def restartMonkey_adb():
	device.shell('am force-close com.android.commands.monkey')
	os.system('adb kill-server')
	os.system('adb start-server')
	time.sleep(2)
	device.shell('am start com.android.commands.monkey')

def CVQ_preset():
	device.shell('logcat -c')
	device.touch(160, 820, MonkeyDevice.DOWN_AND_UP)
	while True:
		logcat2 = device.shell('logcat -d -v time')
		m2 = re.search(r'Time taken for: setting cvs preset', logcat2)
		if m2:
			print "CVQ preset set"
			break
		else:
			time.sleep(1)

def init_state():
	screen = device.shell('dumpsys power | grep mScreenOn=')
	if 'true' in screen:
		print "Screen is on, going to Low Power mode"
		CVQ_preset()
	elif 'false' in screen:
		print "Screen is off, turning on screen"
		device.press('KEYCODE_POWER', MonkeyDevice.DOWN_AND_UP)
		screen = device.shell('dumpsys power | grep mScreenOn=')
		if 'true' in screen:
			print "Screen is on, going to Low Power mode"
			CVQ_preset()

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

def pull_flac(outDir, n):
	print "Starting pull"
	#command = ["bash", "./flac.sh", outDir, flac_name, b]
	#subprocess.call(command, shell=False)
	flacPath='%s/flac/%s.flac' % (outDir, n)
	print flacPath
	combPath='%s/comb/%scomb.pcm' % (outDir, n)
	print combPath
	os.system('adb pull /data/data/com.audience.voiceqmultikeyword/files/flacdumpapp.flac %s' % flacPath )
	os.system('adb pull /data/data/com.audience.voiceqmultikeyword/files/combineddumpapp %s' % combPath )
	print "Ended pull to %s" % outDir

def snooz():
	device.shell('am force-stop com.android.browser')
	device.touch(460, 900, MonkeyDevice.DOWN_AND_UP)
	time.sleep(1)
	CVQ_preset()

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

def asrCase(ASRres, testFolder, outDir):
	fname = os.path.join(outDir, '%s_CVQ.txt' % testFolder)
	f = open(fname, 'w')
	for i in ASRres:
		pattern = re.compile('|'.join(re.escape(key) for key in d.keys()))
		result = pattern.sub(lambda x: d[x.group()], i)
		#uncomment above 2 lines if Utterance number matches n, as dictionary use is irrelevant.
		f.write(''.join(str(result)))
		f.write('\n')
	f.close()
	print fname

def KWcount(value, outDir):
	n = 0
	start_t = time.asctime()
	start = time.time()
	ASRres =[]
	testFolder = '%s_%s_%s_%s' % (Delay, value, FW, VP)
	os.system('mkdir %s/%s' % (outDir, testFolder))
	outDir = '%s/%s' % (outDir, testFolder)
	print "\nStart time: %s, case: %s, test directory: %s" % (start_t, value, outDir)

	while True:
		logcat0 = device.shell('logcat -d -v time')
		try:
			if 'detected cvs event' in logcat0:
				n += 1
				delta_t = time.time() - start
				print "KW detection: %d, Lapsed time: %d" % (n, delta_t)
				b = ' (Utterance_%(n)03d)' % {"n":n}
				asr(ASRres, b)
				pull_flac(outDir, n)
				#comment out above 3 lines for FRR/FA test
				snooz()
			else:
				delta_t = time.time() - start
				if int(delta_t) >= total_t:
					break
		except TypeError:
			asrCase(ASRres, testFolder, outDir)
			adbConnection()
	asrCase(ASRres, testFolder, outDir)
	#frr(value,n, start_t)
	#far(value, n, start_t)




def main():
	init_state()
	for value in case:
		KWcount(value, outDir)
	#f.close()
	# Uncomment above line for FRR/FA test


if __name__ == '__main__':
	signal.signal(signal.SIGINT, exitGracefully)
	main()

