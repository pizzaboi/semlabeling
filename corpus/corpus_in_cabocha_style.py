#! /usr/bin/python
# -*- coding: utf-8 -*-

## convert JFEcorpus to MeCab style.

import argparse
import os

class Morph:
	def __init__(self, line):
		tag, surface, feature, ne = line.strip("\n").split("\t")
		f = feature.split(",")

		self.tag = tag
		self.surface = surface
		self.ne = ne
		self.pos, self.p1, self.p2, self.p3 = f[:4]
		self.cform, self.ctype = f[4:6]
		self.base = f[6]
		self.read = f[7]
		self.pron = f[8]

	def __str__(self):
		return "\t".join((
			self.surface,
			",".join((self.pos, self.p1, self.p2, self.p3,
				self.cform, self.ctype, self.base, self.read, self.pron)),
			self.ne
			))

## normalize directory name
def normalize_dir(_dir):
	return _dir if _dir.endswith("/") else _dir + "/"

## parse arguments
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('src_dir',
		help="source corpus to convert.")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	src_dir = normalize_dir(args.src_dir)
	for src in os.listdir(src_dir):

		S = []
		## make morph list
		for line in open(src_dir + src):
			if not line.startswith(("* ", "#", "EOS")):
				S.append( Morph(line) )
				##print S[-1]

		N = []
		## convert to MeCab-style
		for morph in S:
			if morph.tag.startswith(("O", "C")):
				N.append(morph)
			elif morph.tag.startswith("B"):
				morph.pos = "機能表現"
				morph.p1 = morph.tag.split("-", 1)[1]
				morph.p2, morph.p3 = "*", "*"
				N.append(morph)
			elif morph.tag.startswith("I"):

				## "base" must be updated before "surface"
				N[-1].base = N[-1].surface + morph.base
				N[-1].surface += morph.surface
				N[-1].cform = morph.cform
				N[-1].ctype = morph.ctype
				N[-1].read += morph.read
				N[-1].pron += morph.pron

		## show
		for morph in N:
			print morph

		print












