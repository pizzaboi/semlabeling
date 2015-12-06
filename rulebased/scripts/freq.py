# -*- coding: utf-8 -*-

"""コーパス中の機能表現の出現頻度情報を取得するスクリプト

最長一致法によるベースラインシステムにおいて，意味ラベルの選択に曖昧性がある場合に，
もっとも頻度の高い意味ラベルを選択するための辞書を提供する．
rulebased.py (ベースラインシステムの本体) から呼ばれる．
"""

from collections import defaultdict
import os, sys

class CorpusCounter:

	def __init__(self, corpus):
		self.corpus = os.path.normpath(corpus)

	def count_freq(self):
		"""count_freq() -> dictionary

		corpus内の機能表現と意味ラベルのペアを取得し，頻度情報を辞書にして返す関数．
		"""
		D = defaultdict(lambda : defaultdict(int))
		surface = []
		sem = ""
		for src in os.listdir(self.corpus):
			for line in open(self.corpus + os.sep + src):

				## 機能表現以外は見ない
				if line.startswith(("#", "*", "EOS", "O", "C")):
					continue

				tag, sur = line.split("\t")[:2]
				if tag.startswith("B"):
					## 1つ前の機能表現を辞書に格納
					D["".join(surface)][sem] += 1

					## 現在の機能表現の処理
					## 表層リストの初期化，意味ラベルの取得
					surface = [sur]
					sem = tag.split("-", 1)[1]

				## 先頭以外を表層リストに追加
				elif tag.startswith("I"):
					surface.append(sur)

		return D

	def max_key(self, d):
		"""max_key() -> key

		辞書dの値のうち，最大のvalueをとるときのkeyを返す関数．
		（最も頻度の高い意味ラベルを取得するために使用）
		"""
		return max(d.items(), key=lambda x:x[1])[0]

	def frequent_tags(self):
		"""frequent_tags() -> dictionary

		機能表現別に最も頻度の高い意味ラベルを格納した辞書を返す関数．"""
		freq_dict = self.count_freq()
		ret = {}
		for key in freq_dict.iterkeys():
			ret[key] = self.max_key(freq_dict[key])
		return ret

if __name__ == "__main__":
	corpus = sys.argv[1]

	cc = CorpusCounter(corpus)
	D = cc.frequent_tags()
	for k, v in D.iteritems():
		print k, v
