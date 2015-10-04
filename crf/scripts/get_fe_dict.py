# -*- coding: utf-8 -*-

"""
コーパスから機能表現の表層一覧を取得するスクリプト
"""

import os
import sys

class Morph:

	def __init__(self):
		self.tag = ''
		self.surface = ''
		self.features = ''

def get_fe(corpus):
	fes = set()
	for src in os.listdir(corpus):
		fe = ''
		for line in open(corpus + src):
			if line.startswith(('#', '*', 'EOS')):
				continue

			if line.startswith('B'):
				if fe:
					fes.add(fe)
				fe = ''
				spline = line.strip('\n').split('\t')
				fe += spline[1]

			elif line.startswith('I'):
				spline = line.strip('\n').split('\t')
				fe += spline[1]

			else:
				if fe:
					fes.add(fe)
				fe = ''

	for fe in fes:
		print fe

if __name__ == '__main__':
	corpus = sys.argv[1]
	get_fe(corpus)
