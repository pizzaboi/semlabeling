#! /usr/bin/python
# -*- coding: utf-8 -*-

class Morph:
	def __init__(self):
		self.__surface = None
		self.__features = None
		self.__ne = None

	def set_line(self, line):
		line = line.split("\t")
		self.__surface = line[0]
		self.__features = line[2]

	def surface(self):
		return self.__surface

class TagedMorph(Morph):
	def __init__(self):
		self.__tag = None

	def set_line(self, line):
		line = line.split("\t")
		self.__tag = line[0]
		self.__surface = line[1]
		self.__feature = line[2]

		
## cabocha形式の各文から形態素行をmorphクラスにして返す．
def each_morph(src):
	for line in open(src):
		line = line.strip("\n")
		if line.startswith(("#", "*")):
			pass
		elif line.startswith("EOS"):
			pass
		else:
			morph = Morph()
			morph.set_line(line)
			yield morph

def listfile(fname):
	for f in open(fname):
		yield f.strip("\n")

