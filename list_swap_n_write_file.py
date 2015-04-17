import os
import os.path


outDir = '/home/ate/workspace/es804_CVQ_QS/English/CVQ'
FW = 'LOVE'
VP = 'VPon'
Delay = '10ms'
value = 'Clean'
ASRres = ['Blar (Utterance_001)', 'Hotel (Utterance_002)']
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
    'Utterance_020':'Utterance_199',
}

testFolder = '%s_%s_%s_%s' % (Delay, value, FW, VP)
os.system('mkdir %s/%s' % (outDir, testFolder))

 

def main(ASRres, testFolder):
    fname = os.path.join(outDir, '%s_CVQ.txt' % testFolder)
    f = open(fname, 'w')
    for line in ASRres:
        pattern = re.compile('|'.join(re.escape(key) for key in d.keys()))
        result = pattern.sub(lambda x: d[x.group()], line)
        f.write(''.join(str(result)))
        f.write('\n')
    f.close()
    print f

if __name__ == "__main__":
    main(ASRres, testFolder)



#In case the dictionary keys contain characters like "^", "$" and "/",
#the keys need to be escaped before the regular expression is assembled.
#To do this, .join(d.keys()) could be replaced by .join(re.escape(key) for key in d.keys())
    
