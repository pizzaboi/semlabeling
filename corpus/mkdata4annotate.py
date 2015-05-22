# -*- coding: utf-8 -*-

## make data for annotation
## format:
## OC010000000.txt,morph[,chunktag,sem]

import os
from collections import defaultdict

## class for morphemes.
class Morph:
	def __init__(self, line):
		line = line.split('\t')
		self.surface = line[0]
		self.features = line[1]

	def __repr__(self):
		return '\t'.join(self.surface, '/'.join(self.sense))

## make annotation data from file_list.
def make_data(file_list):
	srcs = [f.strip('\n') for f in open(file_list)]
	for file in srcs:

		## get Morphs per sentence.
		S = []
		path = 'src/team.20130830/OC/' + file.replace('.txt', '.depmod')
		for line in open(path):
			line = line.strip('\n')
			if not line.startswith(('#','*','EOS')):
				S.append(Morph(line))

		## output
		for i in xrange(len(S)):
			print ','.join((file, S[i].surface))
		print ## sentence separator

## sort srcs (file_list) by FEs in the head clause.
def fe_sort(srcs):

	D = defaultdict(list)

	for file in srcs:

		## get FEs in sentence.
		path = 'data/OC_by_CRF/' + file
		fe = []
		fe_list = []
		for line in open(path):
	 		line = line.strip('\n')
	 		if line.startswith(('#','*','EOS', 'O')):
	 			if fe:
	 				fe_list.append(fe)
	 				fe = []
	 		elif line.startswith(('B', 'I')):
	 			fe.append(line.split('\t')[1])

	 	## store the last FEs in the sentence into dictionary.
	 	key = ''.join(fe_list[-1])
	 	D[key].append(file)

 	## sort by keys (=FEs).
 	sorted_srcs = []
 	for k in sorted(D.keys()):
 		for file_name in D[k]:
 			print file_name
 			sorted_srcs.append(fname)

	#print len(sorted_srcs) ## checker
	#print sorted_srcs ## checker
 	return sorted_srcs

## make annotation data with CRF result, sorting by FEs.
def make_data_with_crf_result(file_list):

	## sort files by FE.
	srcs = fe_sort([f.strip('\n') for f in open(file_list)])

	for file in srcs:

		## get Morphs per sentence.
		S = []
		path = 'data/OC_by_CRF/' + file
		for line in open(path):
			line = line.strip('\n')
			if not line.startswith(('#','*','EOS')):
				S.append(Morph(line))

		## output
		for i in xrange(len(S)):
			if ':' in S[i].label:
				chunk_tag = S[i].label.split(':')[0]
				sem_tag = S[i].label.split(':')[1]
			else:
				chunk_tag = ''
				sem_tag = ''
			print ','.join((file, S[i].surface, chunk_tag, sem_tag))
		print ## sentence separator

## make annotation data from 6,362 files without already annotated 1,050 files.
def from_6362_wo_1050():
	file_counter = 0
	for src in os.listdir(corpus_dir):

		## exclude .DS_Store and already annotated 1,050 files.
		if src.startswith('.'):
			continue
		elif src in os.listdir(annotated_dir):
			continue

		## get Morphs per sentence.
		path = corpus_dir + src
		S = []
		for line in open(path):
			line = line.strip('\n')
			if not (line.startswith('#','*','EOS')):
				S.append(Morph(line))

		## output to csv file.
		fo = open('work/out%d.csv' % (file_counter / 1000), 'a')
		file_counter += 1
		for i in xrange(len(S)):
			fo.write(','.join(src,S[i].surface) + '\n')
		fo.write('\n') ## sentence separator

if __name__ == '__main__':
	make_data('corpus/500_l1_u3.lst')
	#make_data_with_crf_result('corpus/500_l1_u3.lst')


