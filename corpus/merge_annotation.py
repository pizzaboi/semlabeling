# -*- coding: utf-8 -*-

## Merge two annotations, and construct corpus, detecting competitives.

import os

## Class for morphems.
class Morph:

	## @param line: morphems from `cabocha -f1` with semantic tag attached at the head.
	def __init__(self, line):
		tag, surface, feature, ne = line.strip('\n').split('\t')
		self.__tag = tag
		self.__surface = surface
		self.__feature = feature
		self.__ne = ne

	## Returns semantic tag.
	def tag(self):
		return self.__tag

	## Returns surface form.
	def surface(self):
		return self.__surface

	## Returns features.
	def feature(self):
		return self.__feature

## Yields file name in annotated 700 files.
def fileiter():
	src_dir = 'data/JFEcorpus_700kanno/' # /JFEcorpus_worker1/ contains non-annotated files.
	for src in os.listdir(src_dir):
		yield src

## Get annotated Morph sequence from file_path.
def annotated_morphs(file_path):
	seq = []
	for line in open(file_path):
		if not line.startswith(('#','*','EOS')):
			seq.append( Morph(line) )
	return seq

## check(m1, m2) is True <=> m1 is the same as m2
## @param m1, m2: Morph Object
def check(m1, m2):

	## Returns False if surface mismatched.
	if m1.surface() != m2.surface():
		return False

	## Returns Flase if features mismatched. 
	if m1.feature() != m2.feature():
		return False

	return True

## Returns one semantic tags, checking relations between two semantic tags.
def sem_tag_checker(t1, t2):

	## t1 denotes it is FE and t2 denotes
	##   it is not FE --> return t1
	##   it is the same FE --> return t1
	##   it is another FE --> raise Error
	##   it is predicate --> raise Error
	if t1.startswith(('B','I')):
		if t2 == 'O' or t1 == t2:
			return t1
		elif t1 != t2:
			return False

	## t1 denotes it is not FE and t2 denotes
	##  it is FE --> return t2
	##  it is predicate --> return t2
	##  it is not FE  --> return t2 ('O')
	elif t1.startswith('O'):
		return t2

	## t1 denotes it is predicate and t2 denotes
	##   it is not FE --> return t1 ('C')
	##   it is predicate --> return t1 ('C')
	##   it is FE --> raise Error
	elif t1 == 'C':
		if t2 == 'O' or t2 == 'C':
			return t1
		else:
			return False

## Yields semantics tags, detecting competing annotations.
def get_tags():
	for file_name in fileiter():

		tags = []

		## get annotated information.
		k = annotated_morphs('data/JFEcorpus_700kanno/' + file_name)
		w = annotated_morphs('data/JFEcorpus_worker1/' + file_name)

		## Raise error if the length of two annotated sequence mismatched.
		if len(k) != len(w):
			raise ValueError("Length mismatched!: %s\n" % file_name)

		## Append semantic tag into the list of tags.
		else:
			for i in xrange(len(k)):

				## Check if two annotated information for morphemes match.
				if not check(k[i], w[i]):
					raise ValueError("Morpheme mismatched!: %s %s\n" % (file_name, k[i].surface()))

				## Get semantic tag, checking two annotated tags.
				t = sem_tag_checker(k[i].tag(), w[i].tag())
				if not t:
					raise ValueError("Tag mismatched!: %s %s\n" % (file_name, k[i].surface()))
				else:
					tags.append(t)

				## アノテーション修正
				# data/JFEcorpus_worker1/OC01_00005m_001.depmod ？: '' --> O 
				# data/JFEcorpus_worker1/OC08_03711m_002.depmod 。: '' --> O
				# data/JFEcorpus_worker1/OC02_00001m_000.depmod すれ: O --> C
				# data/JFEcorpus_worker1/OC02_00001m_000.depmod ば: O --> B-勧め
				# data/JFEcorpus_worker1/OC02_00001m_000.depmod よい: C --> I-勧め
				# data/JFEcorpus_worker1/OC02_01053m_006.depmod て: O --> B-結果状態
				# data/JFEcorpus_worker1/OC02_01053m_006.depmod 入る: C --> I-結果状態
				# data/JFEcorpus_700kanno/OC02_01055m_000.depmod し: C -- > O
				# data/JFEcorpus_700kanno/OC02_01055m_000.depmod たら: B-順接仮定 -- > O

		yield (file_name, tags)

## Merge two annotations, and construct corpus.
def main():
	for file_name, tags in get_tags():
		fo = open('data/JFEcorpus_ver2.1_700_20150526/' + file_name, 'w')
		for line in open('data/JFEcorpus_700kanno/' + file_name):
			if line.startswith(('#', '*', 'EOS')):
				fo.write(line)
			else:
				fo.write(tags.pop(0) + '\t' + line.split('\t', 1)[1])

if __name__ == '__main__':
	main()
