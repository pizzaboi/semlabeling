# -*- coding: utf-8 -*-

## Class for morpheme
class Morph:
	"""Class for morphemes in JFE format.

	If annotated with semantic tags,
	[sem_tag]\t[surface]\t[features]

	else if no annotated, just,
	[surface]\t[features]
	"""
	def __init__(self, line):
		self.__tag     = None
		self.__surface = None
		self.__feature = None
		self.set_line(line)

		self.__ttjsurface  = []
		self.__defined_tag = None
		self.__candidates  = []

	def set_line(self, line):
		line = line.split("\t")

		## if target is annotated with semantic tags
		if len(line) > 3:
			self.__tag     = line[0]
			self.__surface = line[1]
			self.__feature = line[2]

		## if not annotated
		else:
			self.__surface = line[0]
			self.__feature = line[1]

	def tag(self):
		return self.__tag

	def surface(self):
		return self.__surface

	def feature(self):
		return self.__feature

	def candidates(self):
		return self.__candidates

	def ttjsurface(self):
		return self.__ttjsurface

	def defined_tag(self):
		return self.__defined_tag

	def is_fe(self):
		"""is_fe() is True <==> tag is 'B-xxx' or 'I-xxx'."""
		return bool(self.__tag.startswith(("B", "I")))

	def is_tagged(self):
		"""is_tagged() is True <==> defined in longest match principle."""
		return bool(self.__defined_tag)

	def add_candidate(self, cand):
		self.__candidates.append(cand)

	def set_ttjsurface(self, ttjsurface):
		self.__ttjsurface = ttjsurface

	def define_as_begin(self, sem):
		self.__defined_tag = "B-{}".format(sem)

	def define_as_inner(self, sem):
		self.__defined_tag = "I-{}".format(sem)

	def define_as_multi(self, sem):
		self.__defined_tag += "," + sem

	def __str__(self):
		return '%s\t%s\t' % (self.tag, self.surface)

	def __repr__(self):
		res = self.__defined_tag if self.__defined_tag else "O"
		#return self.__surface +"\t" + self.__tag + "\t" + res + "\t" + "/".join([x[0] for x in self.__candidates])
		return self.__tag + "\t" + res