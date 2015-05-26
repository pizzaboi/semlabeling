# -*- coding: utf-8 -*-

## make diff file between bccwj and annotated corpus.
##
## diff file format:
##     # S-ID [filename]
##     [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
##     [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
##     ...
##     [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
##     EOS
##
## morph_length:
##   (ex. 2 for 京都)
## morph_info: morph-parsed result with IPA dic.
##   (ex. 名詞,固有名詞,地域,一般,*,*,京都,キョウト,キョート)
## ne_tag: morph-parsed result.
##   (ex. B-LOCATION)
## sem_tag: annotated semantic tag
##   (ex. B-疑問)

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
def main():
	corpus_dir = 'data/JFEcorpus_ver2.1/'
	srcs = [f for f in os.listdir(corpus_dir) if f != '.DS_Store']
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

if __name__ == '__main__':
	main()