
import re
fname = '/home/ate/workspace/es804_CVQ_QS/English/CVQ/3200ms_Babble6_51747_VPon/3200ms_Babble6_51747_VPon_CVQ.txt'
fname2 = '/home/ate/workspace/es804_CVQ_QS/English/CVQ/3200ms_Babble6_51747_VPon/swapNum_3200ms_Babble6_51747_VPon_CVQ.txt'
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



def main(fname, fname2):
    text = open(fname)
    new_text = open(fname2, 'w')
    for line in text:
        pattern = re.compile('|'.join(re.escape(key) for key in d.keys()))
        result = pattern.sub(lambda x: d[x.group()], line)
        new_text.write(result)
    text.close()
    new_text.close()
    print new_text



if __name__ == "__main__":
    main(fname, fname2)





