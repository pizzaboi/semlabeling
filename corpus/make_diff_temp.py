#! /usr/bin/python
# -*- coding: utf-8 -*-


## 成田さん依頼
## 差分ファイルにいくつかのファイルを追加する．
## めんどうなので1ファイルごとに差分を作成するようにした．
## ファイル名を受け取って差分を出力
## 手作業で全体の差分ファイルに追加

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

def main(src):
	f = open("data/JFEcorpus_ver2.1/" + src)
	print meta_description(src)
	for line in f:
		line = line.strip("\n")
		if line == "EOS":
			print line
		elif not line.startswith(("#", "*")):
			print diff_format(line)

def sort_diff():
	D = {}
	key = ""
	buf = []
	for line in sys.stdin:
		line = line.strip("\n")

		if line.startswith("# "):
			key = line
		elif line.startswith("EOS"):
			buf.append(line)
			if not D.has_key(key):
				D[key] = buf
			else:
				pass
			key = ""
			buf = []
		else:
			buf.append(line)

	for header, contents in sorted(D.iteritems()):
		print header
		for content in contents:
			print content


if __name__ == "__main__":
	#main(sys.argv[1])
	sort_diff()