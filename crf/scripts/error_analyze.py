#! -*- coding: utf-8 -*-

"""
CRFの解析結果のエラー分析をするスクリプト

入力: 評価用ファイル、コーパスディレクトリ、ラベル
出力: 誤りを含む文

idea
・文単位で処理する
　　- 正解、出力、形態素を取得する
　　- エラー分析用に素性も保持したい
・
"""

import os
import sys

class Morph:
	"""形態素クラス．"""

	def __init__(self, gold, output, morph, feature):
		self.__gold   = gold # 正解
		self.__output = output # 出力
		self.__morph   = morph
		self.__feature = feature # 素性

	def is_match(self):
		"""正解ラベルと出力ラベルが一致しているかを判定する関数．"""
		return self.__gold == self.__output

	def morph(self):
		"""形態素の表層形を返す関数．"""
		return self.__morph

	def tag(self, type):
		"""付与されているラベルを返す関数．

		引数によって正解ラベルまたは出力ラベルのみを返す．
		"""
		if type == 'gold':
			return self.__gold
		elif type == 'system':
			return self.__output
		return (self.__gold, self.__output)

	def __str__(self):
		return '\t'.join((self.__gold, self.__output, self.__morph))

class ErrorAnalyzer:

	def __init__(self, corpus, evalf, tag=None):
		self.__corpus = corpus
		self.__eval   = evalf
		self.__target = tag

	def tagiter(self):
		"""評価用ファイルから出力ラベルを取得する関数．"""
		output = [line.strip('\n') for line in open(self.__eval)]
		for t in output:
			if t:
				yield t.split('\t')[1]

	def get_sentence(self):
		"""一文単位で形態素クラスのリストにして返す関数．"""
		output = self.tagiter()
		for src in os.listdir(self.__corpus):
			S = []
			for line in open(self.__corpus + src):
				
				# メタ情報は無視
				if line.startswith(('#','*','EOS')):
					continue

				# 形態素クラス化
				spline = line.strip('\n').split('\t')
				gold = spline[0].replace('C', 'O')
				system = 'O'
				if gold.startswith(('B','I')):
					system = output.next()
				S.append(Morph(gold, system, spline[1], spline[2]))

			yield (src, S)

	def contains_error(self, S):
		"""エラーの有無を判定する関数．"""
		for morph in S:
			if not morph.is_match():
				if not self.__target:
					return 1
				elif morph.tag('gold').endswith(self.__target):
					return 2
				elif morph.tag('system').endswith(self.__target):
					return 3
		return False

	def make_html(self, src, S, error):
		"""HTML形式に変換する関数．

		例：
		[ファイル名] ラベルとして出力
		正解：明日は雨が降る<推量>かもしれない</推量>。
		出力：明日は雨が降る<推量>かも</推量>しれない。
		"""

		# recall, precision表示用の色
		border = {1: 'sentence', 2: 'sentence-red', 3: 'sentence-blue'}
		filename = {1: 'filename', 2: 'filename-red', 3: 'filename-blue'}

		# HTML要素 - 文全体
		div1 = '<div class="%s">' % border[error] \
				+ '<div class="%s">' % filename[error]
		div2 = '<span>%s</span></div>GOLD: %s<br>SYSTEM: %s</div>'

		# HTML要素 - タグ
		start = '<span class="fe"><span class="semtag">&lt;%s&gt;</span>'
		hstart = '<span class="fe-colored"><span class="semtag">&lt;%s&gt;</span>'
		end   = '<span class="semtag">&lt;/%s&gt;</span></span>'

		body = {'gold': '', 'system': ''}
		for i in xrange(len(S)):

			for tagtype in ('gold', 'system'):

				tag = S[i].tag(tagtype)

				# 機能表現の開始前で，前にHTMLタグを追加
				if tag.startswith('B'):
					tag_name = tag.split('-', 1)[1]
					if tag_name.endswith(self.__target):
						body[tagtype] += hstart % tag_name + S[i].morph()
					else:
						body[tagtype] += start % tag_name + S[i].morph()

					# 後ろをチェックして，同じ機能表現でないときは終了タグを追加
					if i + 1 < len(S):
						if not S[i + 1].tag(tagtype).startswith('I'):
							body[tagtype] += end % tag_name
					else:
						body[tagtype] += end % tag_name

				# 機能表現の終了時に，後ろにHTMLタグを追加
				elif tag.startswith('I'):
					tag_name = tag.split('-', 1)[1]
					if i + 1 < len(S):
						if not S[i + 1].tag(tagtype).startswith('I'):
							body[tagtype] += S[i].morph() + end % tag_name
						else:
							body[tagtype] += S[i].morph()
					else:
						body[tagtype] += S[i].morph() + end % tag_name

				else:
					body[tagtype] += S[i].morph()

		print div1 + div2 % (src, body['gold'], body['system'])

	def main(self):
		head = """
		<!DOCTYPE HTML>
		<html>
		<head>
		<meta charset="UTF-8">
		<link rel="stylesheet" href="css/error_analyze.css"/>
		</head>
		<body>
		<div class="container">
		"""
		
		tail = """
		</div>
		</body>
		</html>"""

		print head

		for src, S in self.get_sentence():
			error = self.contains_error(S)
			if error:
				self.make_html(src, S, error)

		print tail

if __name__ == '__main__':
	corpus = sys.argv[1]
	evalf = sys.argv[2]
	tag = sys.argv[3]
	ea = ErrorAnalyzer(corpus, evalf, tag)
	ea.main()
