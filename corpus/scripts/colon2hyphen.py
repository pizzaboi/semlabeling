# -*- coding: utf-8 -*-

import argparse
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

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('colon', type=str, help="coloned corpus.")
	parser.add_argument('dst', type=str, help="destination of corpus.")
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()

	## 変換元コーパスの検証
	corpus = os.path.normpath(args.colon) + os.sep
	if not os.path.isdir(corpus):
		sys.stderr.write("Invalid source: %s\n" % corpus)
		sys.exit(0)

	## 変換先コーパスの検証
	dst = os.path.normpath(args.dst) + os.sep
	if not os.path.isdir(dst):
		os.mkdir(dst)

	convert(corpus, dst)




