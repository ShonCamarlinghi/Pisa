import os, sys, time

total_t = 10
case = ['Clean']
outDir = '/Users/scamarlinghi/workspace/Siri_WakeupTest'
siriLog = os.path.join(outDir, 'siriLog.txt')
cmd = 'idevicesyslog >> ' + siriLog
#os.system('idevicesyslog >> '+ outDir + ' siriLog.txt')
os.system(cmd)



class Logger(object):
    def __init__(self, filename = 'Default.log'):
        self.terminal = sys.stdout
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

def seraSera(value):
    f = os.path.join(outDir, value + '.txt')
    print f
    sys.stdout = Logger(f)
    start_t = time.asctime()
    start = time.time()
    print "============================================================="
    print "\nCase: %s \nStart time: %s " % (value, start_t)
    print "============================================================="

    while True:
        os.system('tail -f /Users/scamarlinghi/workspace/Siri_WakeupTest/siriLog.txt  >> ' + f)
        #os.system('idevicesyslog -d | grep Siri')
        delta_t = time.time() - start
        if int(delta_t) >= total_t:
            break
    print "============================================================="
    print "\nCase: %s \nStart time: %s \nEnd time: %s" % (value, start_t, time.asctime())
    print "============================================================="


def main():
    for value in case:
        seraSera(value)


if __name__ == '__main__':
    main()




