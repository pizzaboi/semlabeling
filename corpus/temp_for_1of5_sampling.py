# -*- coding: utf-8 -*-

import random

## リストUからN件をサンプリングしたリストを返す
def sampling(U, N):
    for i in xrange(N):
        index = random.randint(N, len(U)-1)
        U[i], U[index] = U[index], U[i]
    return sorted(U[:N])



import argparse
import os, sys

## Returns file ID in String.
def meta_description(file_name):
	return "# S-ID {}".format(file_name.replace('.depmod', ''))

## Returns length of morpheme in Int.
def morph_boundary(morph):
	return len(unicode(morph))

## Convert line to diff file format.
def diff_format(line):
	sem_tag, morph, features, ne_tag = line.split('\t')
	return '\t'.join(
		(str(morph_boundary(morph)), features, ne_tag, sem_tag))

## Main process.
def main(corpus_dir):
	srcs = sampling([f for f in os.listdir(corpus_dir) if f != '.DS_Store'], 147)
	for src in srcs:

		f = open(corpus_dir + src)

		## print meta_description per file.
		print meta_description(src)

		## print diff information for each morpheme-lines.
		for line in f:
			line = line.strip('\n')
			if line == 'EOS':
				print line
			elif not line.startswith(('#', '*')):
				print diff_format(line)

## Parse arguments.
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('corpus', type=str)
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	args = parse_args()
	main(args.corpus)