#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import math
import random

## Class for FE sequence.
class FESeq:
	def __init__(self, src, fe, sem):
		self.src = src.split("/")[-1]
		self.fe = "".join(fe)
		self.fe_len = len(fe)
		self.sem = sem

	def __str__(self):
		return "%s: %s" % (self.src, self.fe)

	## contains() is True <=> FE sequence contains [pattern].
	def contains(self, patterns):
		for pattern in patterns:
			if pattern in self.fe:
				return True
		return False

	## contains_sem() is True <=> FE sequence contains [sem_labels].
	def contains_sem(self, sem_labels):
		for sem_label in sem_labels:
			if sem_label in self.sem:
				return True
		return False

class Sampler:
	def __init__(self):
		pass

	## Sampling N instances from U, returning result in list.
	def sampling(self, U, N):
		if len(U) <= N:
			return U
		for i in xrange(N):
			index = random.randint(N, len(U)-1)
			U[i], U[index] = U[index], U[i]
		return sorted(U[:N])

	## s_list から e_list を除いた num をサンプリングする．
	def conditional_sampling(self, s_list, e_list, num, by_num=False):

		# サンプル数
		s_size = len(s_list)
		sampling_size = num if by_num else int(math.ceil(s_size * num * 0.01))

		# サンプリング対象
		t_list = list(set(s_list) - set(e_list))

		# サンプリング
		t_len = len(t_list) - 1
		return self.sampling(t_list, sampling_size)

	## Sampling sentences by the length of last FE sequence.
	def morph_sampling(self, parsed_oc, lower, upper, num):

		## Get the last FE sequence object.
		def last_fe(src):
			fe = []
			sem = []
			for line in open(src):
				if line.startswith(("#", "*")):
					pass
				elif line.startswith("EOS"):
					return FESeq(src, fe, sem)
				else:
					fields = line.split("\t")
					if line.startswith("B"):
						fe.append(fields[1])
						sem.append(fields[0].split(":", 1)[1])
					elif line.startswith("I"):
						fe.append(fields[1])
					else:
						if fields[2].split(",")[0] != "記号":
							fe = []
							sem = []

		morph_filtered = []
		for src in os.listdir(parsed_oc):
			target = last_fe(parsed_oc + src)
			if lower <= target.fe_len < upper:
				morph_filtered.append(target.src)

		only_new = []
		past_set = [f.replace(".depmod", ".txt") for f in os.listdir("data/JFEcorpus_ver2.0_append/")]
		for i, item in enumerate(morph_filtered):
			if not item in past_set:
				only_new.append(item)

		return self.sampling(only_new, num)

def parse_args():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()

	parser_a = subparsers.add_parser("conditional")
	parser_a.add_argument("-s", "--src", type=str, help="target directory")
	parser_a.add_argument("-p", "--percentage", type=int, help="percentage")
	parser_a.add_argument("-e", "--exempt", type=str, help="exception list")
	parser_a.add_argument("-n", action="store_true")

	parser_b = subparsers.add_parser("morph")
	parser_b.add_argument("--parsed_oc", type=str,
						default="data/OC_by_CRF/",
						help="directory of parsed OC")
	parser_b.add_argument("-l", "--lower", type=int, default=0,
						help="lower bound of morphemes")
	parser_b.add_argument("-u", "--upper", type=int, default=100,
						help="upper bound of morphemes")
	parser_b.add_argument("-s", "--size", type=int, default=10000)

	return parser.parse_args()
	
if __name__ == "__main__":
	args = parse_args()
	#print args

	s = Sampler()

	if hasattr(args, "parsed_oc"):
		ret = s.morph_sampling(args.parsed_oc, args.lower, args.upper, args.size)

	else:
		if os.path.isdir(args.src):
			s_list = os.listdir(args.src)
		else:
			s_list = [f.strip("\n") + ".depmod" for f in open(args.src)]
		e_list = [f.strip("\n") + ".depmod" for f in open(args.exempt)]

		ret = s.conditional_sampling(s_list, e_list, args.percentage, by_num=args.n)

	for x in ret:
		print x
	#print len(ret)