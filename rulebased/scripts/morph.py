# -*- coding: utf-8 -*-

import sys

class Morph:
	"""形態素クラス．

	CaboCha形式の単語情報を受け取り，形態素クラスを構築する．
	入力として受け取る単語情報は，以下のいずれかのフォーマットを想定．

	i) デフォルトの形態素解析結果
		かも\t助詞,副助詞,*,*,*,*,かも,カモ,カモ

	ii) 先頭に意味ラベルが付与された形態素解析結果
		B-推量―不確実\tかも\t助詞,副助詞,*,*,*,*,かも,カモ,カモ

	* 単語素性部分の内容は考慮しない．
	* 固有表現タグの有無に対応する．
	"""

	def __init__(self, line):
		## 基本項目
		self.__tag     = None
		self.__surface = None
		self.__feature = None

		## 基本項目の設定
		self.set_line(line)

		## 最長一致法による解析時に使用する項目
		self.__ttjsurface  = []
		self.__defined_tag = None
		self.__candidates  = []

	def set_line(self, line):
		"""set_line() -> None

		単語情報の要素数を元に，形態素クラスの基本項目を設定する関数．"""
		spl = line.split("\t")

		## 機能表現タグあり，固有表現タグありの場合
		if len(spl) == 4 or (len(spl) == 3 and spl[2].find(',') > 0):
			self.__tag     = spl[0]
			self.__surface = spl[1]
			self.__feature = spl[2]

		## 機能表現タグなし，固有表現タグなしの場合
		elif len(spl) == 2 or (len(spl) == 3 and spl[1].find(',') > 0):
			self.__surface = spl[0]
			self.__feature = spl[1]

		else:
			sys.stderr.write("Invalid format: %s\n" % line)
			sys.exit(0)

	def tag(self):
		"""tag() -> string"""
		return self.__tag

	def surface(self):
		"""surface() -> string"""
		return self.__surface

	def feature(self):
		"""feature() -> string"""
		return self.__feature

	def candidates(self):
		"""candidates() -> list"""
		return self.__candidates

	def ttjsurface(self):
		"""ttjsurface() -> list"""
		return self.__ttjsurface

	def defined_tag(self):
		"""defined_tag() -> string"""
		return self.__defined_tag

	def is_fe(self):
		"""is_fe() -> boolean

		機能表現タグがBまたはIで始まるときTrueを返す関数．"""
		return bool(self.__tag.startswith(("B", "I")))

	def is_tagged(self):
		"""is_tagged() -> boolean

		最長一致法によって機能表現タグが設定済みのときTrueを返す関数．"""
		return bool(self.__defined_tag)

	def add_candidate(self, cand):
		"""add_candidate() -> None"""
		self.__candidates.append(cand)

	def set_ttjsurface(self, ttjsurface):
		"""set_ttjsurface() -> None"""
		self.__ttjsurface = ttjsurface

	def define_as_begin(self, sem):
		"""define_as_begin() -> None"""
		self.__defined_tag = "B-{}".format(sem)

	def define_as_inner(self, sem):
		"""define_as_inner() -> None"""
		self.__defined_tag = "I-{}".format(sem)

	def define_as_multi(self, sem):
		"""define_as_multi() -> None"""
		self.__defined_tag += "," + sem

	def __str__(self):
		return "FE_TAG:%(fe_tag)s\tSURFACE:%(surface)s\tFEATURE:%(feature)s" % {
			'fe_tag' : self.__tag,
			'surface': self.__surface,
			'feature': self.__feature
		}

	def __repr__(self):
		system_tag = self.__defined_tag if self.__defined_tag else 'O'
		return self.__tag + '\t' + system_tag

if __name__ == '__main__':

	## テスト
	print Morph("かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ")
	print Morph("かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ	NE_TAG")
	print Morph("B-推量-不確実	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ")
	print Morph("I-推量-不確実	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ")
	print Morph("O	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ")
	print Morph("B-推量-不確実	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ	NE_TAG")
	print Morph("I-推量-不確実	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ	NE_TAG")
	print Morph("O	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ	NE_TAG")






