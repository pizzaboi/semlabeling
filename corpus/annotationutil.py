#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import csv
import sys
import os

import slutil

def normalize_dst(dst):
	if not dst.endswith("/"):
		dst += "/"
	if not os.path.isdir(dst):
		os.makedirs(dst)
	return dst

class Morph:
	def __init__(self):
		self.__filename = None
		self.__surface = None
		self.__chunk = None
		self.__sem = None
		self.__features = None 

	def row2morph(self, row):
		self.__filename = row[0].replace(".txt", ".depmod")
		self.__surface = row[1]
		self.__chunk = row[2]
		self.__sem = self.sem_filter(row[3])

	def line2morph(self, line):
		line = line.split("\t")
		self.__surface = line[0]
		self.__features = line[1]

	## Convert labels ver.2.0 to ver.2.1.
	def sem_filter(sem, label):
		if label == "確認": return "疑問"
		elif label == "過去": return "完了"
		elif label == "命令": return "依頼"
		elif label == "限定": return "程度"
		else:
			return label

	## Returns True <=> chunk tag is I.
	def is_inner(self):
		return bool(self.__chunk == "I")

	## Returns True <=> chunk tag is C.
	def is_predicate(self):
		return bool(self.__chunk == "C")

	## Returns True <=> chunk tag is O or blank.
	def is_other(self):
		return bool(self.__chunk in ("O", ""))

	## Returns source file name.
	def filename(self):
		return self.__filename

	## Returns surface.
	def surface(self):
		return self.__surface

	## Returns semantic meaning.
	def sem(self):
		return self.__sem

	def set_sem(self, sem):
		self.__sem = sem

	## Returns semantic label.
	def label(self, sep):
		if self.is_other(): return "O"
		if self.is_predicate(): return self.__chunk
		return sep.join((self.__chunk, self.__sem))

## Convert csv_file to BCCWJ-styled corpus.
def csv2corpus(args):
	csv_file = args.csv_file
	dst_dir = args.dst_dir
	sep = args.sep
	reader = csv.reader(open(csv_file, "U"), delimiter=",")
	morphs = []
	try:
		for row in reader:
			if not row[0]:
				## Update tags
				for i in xrange(len(morphs) - 1):
					if morphs[i].is_inner():
						morphs[i].set_sem(morphs[i-1].sem())

				## Output
				fi = open("src/team.20130830/OC/" + morphs[0].filename())
				fo = open(normalize_dst(dst_dir) + morphs[0].filename(), "w")
				for line in fi:
					if line.startswith(("#", "*", "EOS")):
						#print line.strip("\n")
						fo.write(line)
					else:
						m = morphs.pop(0)
						#print m.label(sep) + "\t" + line.strip("\n")
						fo.write(m.label(sep) + "\t" + line)
				morphs = []

			elif row[0].startswith("OC"):
				morph = Morph()
				morph.row2morph(row)
				morphs.append(morph)

	except csv.Error, e:
		sys.exit("File {}, line {}: {}".format(src, reader, e))


def make_sheet(args):
	for src in slutil.listfile(args.src):
		path = "src/team.20130830/OC/" + src.replace(".txt", ".depmod")
		for morph in slutil.each_morph(path):
			print ",".join((src, morph.surface()))
		print

def parse_args():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()

	parser_a = subparsers.add_parser("csv2corpus")
	parser_a.add_argument("csv_file", type=str, help="Annotated csv file, utf-8")
	parser_a.add_argument("dst_dir", type=str)
	parser_a.add_argument("-s", "--sep", type=str, default="-")
	parser_a.add_argument("-p", "--pre", action="store_true")
	parser_a.set_defaults(func=csv2corpus)

	parser_b = subparsers.add_parser("sheet")
	parser_b.add_argument("src")
	parser_b.set_defaults(func=make_sheet)

	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	args.func(args)




