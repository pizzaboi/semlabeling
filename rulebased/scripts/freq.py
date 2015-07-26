#! /usr/bin/python
# -*- coding: utf-8 -*-

##
## 機能表現ごとに付与されるラベルの頻度をカウントする．
##

import collections
import os

class CorpusCounter:
	def __init__(self):
		pass

	## 機能表現別に意味ラベルの頻度を返す関数．
	def count_freq(self, corpus):
		D = collections.defaultdict(lambda : collections.defaultdict(int))
		surface = []
		sem = ""
		for src in os.listdir(corpus):
			for line in open(corpus + src):
				if line.startswith(("#", "*", "EOS", "O", "C")):
					continue

				tag, sur = line.split("\t")[:2]
				if tag.startswith("B"):
					## 1つ前の機能表現の処理
					D["".join(surface)][sem] += 1

					## 現在の機能表現の処理
					surface = [sur]
					sem = tag.split("-", 1)[1]
				elif tag.startswith("I"):
					surface.append(sur)
		return D

	## 辞書の値の最大値を持つkeyを返す関数．
	def max_key(self, _dict):
		return max(_dict.items(), key=lambda x:x[1])[0]

	## 機能表現別に最も頻度の高い意味ラベルを格納した辞書を返す関数．
	def frequent_tags(self, corpus):
		freq_dict = self.count_freq(corpus)
		ret = {}
		for key in freq_dict.iterkeys():
			ret[key] = self.max_key(freq_dict[key])
		return ret

if __name__ == "__main__":
	corpus = "data/JFEcorpus_ver2.1/"

	cc = CorpusCounter()
	print len(cc.frequent_tags(corpus))
