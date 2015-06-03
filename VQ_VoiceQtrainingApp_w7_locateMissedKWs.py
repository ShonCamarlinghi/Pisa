#!/usr/bin/python/2.7
import time
import sys
import os
import os.path
import re
import signal


from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice


#################################################################################################
total_n = 40.0  # number of KWs per case
total_t = 600  # length  of each case in seconds
spacing = 14
last_delta_plus = int(round(total_n*spacing-spacing/2.3+spacing))
case = ['Clean']  # 'Car0', 'Babble0', 'Car6', 'Babble6', 'Car12', 'Babble12']  # test cases
outDir = 'C:\Users\scamarlinghi\Documents\CVQ\CVQ_Dragonboard'  # output directory
FW = '51747'  # test FW
KW = 'U4_K4_Ch_NewTraining'  # test KW
fname = os.path.join(outDir, KW + '_VQ.txt')
##################################################################################################

os.system('adb root')
time.sleep(2)
os.system('adb remount')
time.sleep(3)
adb = os.popen('adb devices').read().strip().split('\n')[1:]
deviceID = adb[0].split('\t')[0]
device = MonkeyRunner.waitForConnection(1000, deviceID)
print 'Device s/n: %s' % deviceID


try:
    currentDeviceX = float(device.getProperty("display.width"))
    currentDeviceY = float(device.getProperty("display.height"))
    print "X = %s, Y = %s" % (currentDeviceX, currentDeviceY)
except TypeError:
    print "failed to get screen size, pls to restart script"
    device.shell('am force-close com.android.commands.monkey')
    sys.exit(1)

def transX(x):
    ''' (number) -> intsvd
    TransX takes the x value supplied from the original device
    and converts it to match the resolution of whatever device
    is plugged in
    '''
    originalWidth = 540;
    #Get X dimensions of Current Device
    xScale = (currentDeviceX)/(originalWidth)
    x = xScale * x
    return int(x)


def transY(y):
    ''' (number) -> int
    TransY takes the y value supplied from the original device
    and converts it to match the resolution of whatever device
    is plugged in.
    '''
    originalHeight = 960;
    #Get Y dimensions of Current Device
    yScale = (currentDeviceY)/(originalHeight)
    y = yScale * y
    return int(y)

def adbConnection(value, outDir):
    global device
    try:
        device.shell('am force-close com.android.commands.monkey')
        time.sleep(1)
        device.shell('am start com.android.commands.monkey')
        device = MonkeyRunner.waitForConnection(3, deviceID)
        print 'Connected to device: %s' % deviceID
        #KWcount(value, outDir)
    except IndexError:
        print 'Could not get adb connection at %s, is your device off/rebooting?' % time.asctime()
        sys.exit(1)

def exitGracefully(signum, frame):
    print 'Exiting Gracefully...'
    signal.signal(signal.SIGINT, signal.getsignal(signal.SIGINT))
    device.shell('am force-close com.android.commands.monkey')
    sys.exit(1)

def cvq_preset():
    device.shell('logcat -c')
    time.sleep(1)
    device.shell('input tap %d %d' % (transX(160), transY(820)))
    while True:
        logcat2 = device.shell('logcat -d -v time')
        m2 = re.search(r'Time taken for: setting cvs preset', logcat2)
        if m2:
            print "CVQ preset set"
            break
        else:
            time.sleep(1)

def snooz():
    logcat_init = device.shell('logcat -d -v time')
    m00 = re.search(r'Displayed com.audience.voiceqmultikeyword/.PerformActionActivity', logcat_init)
    if m00:
        device.shell('input keyevent KEYCODE_BACK')
        print "Tapping back from KWdetection page... Going to Low Power mode..."
        cvq_preset()
    else:
        print "Going to Low Power mode"
        cvq_preset()

def init_state():
    screen = device.shell('dumpsys power | grep mScreenOn=')
    if 'true' in screen:
        print "Screen is on"
        snooz()
    elif 'false' in screen:
        print "Screen is off, turning on screen"
        device.press('KEYCODE_POWER', MonkeyDevice.DOWN_AND_UP)
        screen = device.shell('dumpsys power | grep mScreenOn=')
        if 'true' in screen:
            print "Screen is on, going to Low Power mode"
            cvq_preset()

def frr(value, n, start_t, data):
    global i
    d = {}
    for i in range(1, 6):
        d[i]=0
    f = open(fname, 'a')
    z = (total_n - n) / total_n * 100
    f.write("\nNoise: %s, KW detect count: %d, FRR rate: %.2f" % (value, n, round(z, 2)))
    f.write("\nStart time: %s" % (start_t))
    f.write("\nEnd time: %s" % (time.asctime()))
    for key in data:
        if data[key][0] in d.keys():
            d[data[key][0]] += 1
    f.write("\nKW ID: number of triggers:  ")
    f.write(str(d))

    for i in data.keys():
        oi = round(data[i][1])
        if i < len(data.keys()):
            x = round(data[i+1][1] - oi)
            if x > spacing:
                miss = x//spacing - 1
                if miss > 0:
                    f.write("\nMissed %d before KW detect %d" %(miss, i+1))
        if n == i:
            w = round(last_delta_plus - oi)
            missEnd = w//spacing -1
            if missEnd > 0:
                f.write("\nMissed %d last KWs" % missEnd)
        if len(data.keys()) == 1 and oi > spacing:
            w = round(last_delta_plus - oi)
            miss = oi//spacing
            f.write("\nMissed %d before KW detect %d" %(miss, i))
            if w > spacing:
                missEnd = w//spacing - 1
                f.write("\n and %d last KW" % missEnd)
    f.write("\nMissed %d KWs total out of %d.\n" % ((total_n - n), total_n))
    f.write(str(data))
    f.write("\n==================================================\n\n")
    #if n < total_n:
    #    for i in range(n+1, total_n+1):
    #        data[i]=(None, None)
    f.close()

def far(value, n, start_t, data):
    f = open(fname, 'a')
    f.write("Noise: %s, KW detect count: %d" % (value, n))
    f.write("\nStart time: %s" % (start_t))
    f.write("\nEnd time: %s \n" % (time.asctime()))
    f.write("\n==================================================\n\n")
    f.close()

def KWcount(value, outDir):
    data = {}
    n = 0
    start_t = time.asctime()
    start = time.time()
    print "\nStart time: %s, case: %s, test directory: %s" % (start_t, value, outDir)
    while True:
        logcat0 = device.shell('logcat -d -v time')
        try:
            m = re.search('detected cvs event', logcat0)
            if m:
                n += 1
                delta_t = int(time.time() - start)
                #print m.group()
                a = re.split(r' 258 : 2 : (.*)', logcat0)
                #print type(a)
                #a = a.rstrip('\r')
                #print a
                KW_ID = a[-2][-1]
                print " KW detection: %d \n KW_number: %s \n Lapsed time: %d" % (n, KW_ID, delta_t )
                data[n] = KW_ID, delta_t
                time.sleep(2)
                snooz()
            else:
                delta_t = time.time() - start
                if int(delta_t) >= total_t:
                    break
        except TypeError:
            if delta_t < total_t:
                print "Broken adb link. \nTest stopped on %d second" % delta_t
                frr(value, n, start_t, data)
                #far(value, n, start_t, data)
                device.shell('am force-close com.android.commands.monkey')
                time.sleep(1)
                sys.exit(1)
    frr(value, n, start_t, data)
    #far(value, n, start_t, delta_t, data)

def main():
    init_state()
    for value in case:
        KWcount(value, outDir)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exitGracefully)
    main()

