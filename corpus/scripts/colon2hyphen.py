# -*- coding: utf-8 -*-

import os
import sys

"""コロン形式 --> ハイフン形式への変換"""


def convert(corpus, target):
	for f in os.listdir(corpus):
		fi = open(corpus + f)
		fo = open(target + f, 'w')
		for line in fi:
			line = line.strip('\n')
			if line.startswith(('#','*','EOS')):
				fo.write(line + '\n')
			else:
				spline = line.split('\t', 1)
				fo.write(spline[0].replace(':', '-') + '\t' + spline[1] + '\n')

if __name__ == '__main__':
	corpus = sys.argv[1]
	target = sys.argv[2]

	cmd = 'mkdir %s' % target
	os.system(cmd)

	convert(corpus, target)




