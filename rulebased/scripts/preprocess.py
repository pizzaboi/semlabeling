# -*- coding: utf-8 -*-

from collections import defaultdict
import kyotocabinet
from morph import Morph
import os

class AdditionalEntryCollector:

	def __init__(self, corpus, ttj):
		self.corpus = os.path.normpath(corpus)
		self.ttj = read_db(ttj)

	def triplet_extractor(self, S):
		"""triplet_extractor() -> (list of string, string, string)

		Morphクラスのリストから，機能表現の表層・意味ラベル・接続情報の組をすべて抽出する関
		数．表層は形態素のリスト，接続情報はひとつ前の形態素の単語素性．
		"""
		surface = []
		label = ''
		constraint = ''
		for i, morph in enumerate(S):
			if morph.tag().startswith('B'):

				## ひとつ前の機能表現に対する処理
				if surface:
					yield (surface, label, constraint)

				surface = [morph.surface()]
				label = morph.tag().split('-', 1)[1] # 意味カテゴリを取得
				constraint = S[i-1].feature()        # 接続情報の取得

			elif morph.tag().startswith('I'):
				surface.append(morph.surface())

		if surface:
			yield (surface, label, constraint)

	def dict_has(self, surface, label):
		"""dict_has() -> bool

		『つつじ』に同じエントリが存在するかを判定する関数．
		先頭形態素版core2seqを検索して，意味ラベルと周辺形態素の一致を検証する．どちらも
		一致した場合のみTrueを返す．
		"""
		entries = self.ttj.get(surface[0])

		if not entries:
			return False

		for entry in entries.split('/'):
			e = entry.split(',')
			sec, ttj, seq = e[0], e[1], e[2:]

			## 意味ラベルが異なる場合は次のエントリへ
			if sec != label:
				continue

			## 意味ラベルが一致したら周辺形態素を検証
			for item in seq:
				## 形態素が1つだけならTrue
				if not item:
					return True

					num = int(item.split(':')[0])
					## 形態素数が違うときは次のエントリへ
					if not num in xrange(len(surface)):
						break
					## 表層が不一致ならば次のエントリへ
					if surface[num] != item.split(':')[1]:
						break
			## 意味ラベルと周辺形態素が一致したらTrue
			else:
				return True

		## 一致するエントリがなければFalse
		return False

	def fe2str(self, surface, label, append_id):
		"""fe2str() -> string

		追加機能表現の文字列形式を返す関数．
		@param surface   : 機能表現表層, list of str
		@param label     : 意味ラベル, str
		@param append_id : 追加ID, int
		"""
		return '%(head)s\tx00:%(label)s,APPEND%(id)d:%(surface)s,%(parts)s' % {
			'head' : surface[0],
			'label': label,
			'id'   : append_id,
			'surface': '.'.join(surface),
			'parts' : ''.join(['%d:%s,' % (i+1,m) for i,m in enumerate(surface[1:])])
		}

	def cc2str(self, constraints, append_id):
		"""cc2str() -> string

		追加接続制約の文字列形式を返す関数．
		@param constraints : 接続制約, list of str
		@param append_id   : 追加ID, str
		"""
		return 'APPEND%(id)d\t%(constraints)s' % {
			'id' : append_id,
			'constraints' : ';'.join(set(constraints))
		}

	def get_add_entry(self):
		"""get_add_entry() -> (list, list)

		追加機能表現・追加接続制約を取得する関数．"""
		D = defaultdict(lambda : defaultdict(list))
		for src in os.listdir(self.corpus):

			## Morphクラスのリストを作成
			S = []
			for line in open(self.corpus + os.path.sep + src):
				line = line.strip('\n')
				if not line.startswith(('#','*','EOS')):
					S.append(Morph(line))

			## 機能表現を抽出
			for surface, label, contraints in self.triplet_extractor(S):
				if not self.dict_has(surface, label):
					## 新しい機能表現ならば，辞書に追加
					D['.'.join(surface)][label].append(contraints)

		## 追加機能表現，追加制約用の辞書を構築
		F, C = [], []
		append_id = 0
		for surface, D_label in D.iteritems():
			for label, constraints in D_label.iteritems():
				F.append(self.fe2str(surface.split('.'), label, append_id))
				#print self.fe2str(surface.split('.'), label, append_id)
				C.append(self.cc2str(constraints, append_id))
				#print self.cc2str(constraints, append_id)

				append_id += 1
				#print surface + '\t' + label + '\t' + ','.join(constraints)
		return F, C

def read_db(DB):
    """read_db() -> kyotocabinet format database

    kyotocabinet形式のデータベースを読み込む関数．"""
    db = kyotocabinet.DB()
    if not db.open(DB, kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE):
        sys.stderr.write('ERROR: failed to open: %s\n' % db.error())
    return db

def set_db(DB, key, value):
    """set_db() -> None

    kyotocabinet形式のデータベースに要素を追加する関数．"""
    db = kyotocabinet.DB()
    if not db.open(DB, kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE):
        sys.stderr.write('ERORR: failed to open: %s\n' % db.error())
    db.set(key, value)
    if not db.close():
        sys.stderr.write('ERROR: failed to close: %s\n' % db.error())

class DictCompiler:

	def __init__(self):
		pass

	def exchange_core(self, older):
		"""exchange_core() -> (string, string)

		core2seq形式のエントリ受け取り，keyを先頭形態素にしたエントリを返す関数．
		"""
		older = older.strip('\n').split('\t')
		entries = older[1].split('/')
		for entry in entries:
			e = entry.split(',')
			surface = e[1].split(':')[1].split('.')

			## 新しいエントリを作成
			key = surface[0]
			morphs = ','.join(['%d:%s' % (i+1, c) for i, c in enumerate(surface[1:])])
			return (key, ','.join(e[:2]) + ',' + morphs)

	def build_ttj(self, db_name, core2seq):
		"""build_ttj() -> None

		core2seq形式の『つつじ』をkeyを先頭形態素に変換して，kyotocabinet形式の辞書に
		変換する関数．
		"""
		D = defaultdict(list)
		for entry in open(core2seq):
			k, v = self.exchange_core(entry)
			D[k].append(v)

		for k, v in D.iteritems():
			set_db(db_name, k, '/'.join(v))

	def extended_dict(self, core2seq, add_dict):
		"""extended_dict() -> dictionary

		core2seq形式の『つつじ』と，追加機能表現の辞書を統合して辞書を返す関数．
		"""
		D = defaultdict(list)
		## 『つつじ』エントリを追加
		for entry in open(core2seq):
			k, v = self.exchange_core(entry)
			D[k].append(v)

		## 追加機能表現を追加
		for line in add_dict:
			spl = line.strip('\n').split('\t')
			D[spl[0]].append(spl[1])

		return D

## 接続制約辞書の構築
class ConstraintCompiler:

	def __init__(self, connectID, rule_list):
		self.connectID = connectID
		self.rule_list = rule_list

	def expand_origin(self):
		"""expand_origin() -> dictionary

		connectID.txtに記載されている接続制約を辞書化する関数．
		IDで参照する接続制約をすべて展開して辞書化．
		"""
		constraints = defaultdict(list)
		## 接続情報IDと接続情報ペアのデータを辞書化
		for line in open(self.connectID):
			spl = line.strip('\n').split('\t')
			constraints[spl[0]] = [spl[1]]

		## 接続情報中に別の接続情報IDが含まれている場合，展開する
		for _id, cs in constraints.iteritems():
			cs = cs[0].split(';')
			while any(c.isalnum() for c in cs):
				expanded = []
				for c in cs:
					if c.isalnum():
						expanded.extend(constraints[c])
					else:
						expanded.append(c)
				cs = expanded
			constraints[_id] = cs

		return constraints

	def map_ttjid2constraint(self):
		"""map_ttjid2constraint() -> dictionary

		つつじIDから接続情報へのマッピングを行う関数．
		つつじIDをkey，接続情報をvalueとする辞書を構築して返す．
		"""
		D = {}
		constraints = self.expand_origin()
		for line in open(self.rule_list):
			ttjid, fe, left, right = line.strip('\n').split(',')
			D[ttjid] = constraints[left[0:2]]

		return D

	def map_append2constraints(self, D, appendix):
		"""map_append2constraints() -> dictionary

		接続制約辞書に，追加接続制約を追加する関数．
		"""
		for line in appendix:
			_id, constraints = line.strip('\n').split('\t')
			D[_id] = constraints.split(';')

		return D

	def get_dictionary(self, appendix):
		## 既存の接続制約を辞書化
		D = self.map_ttjid2constraint()

		## 追加機能表現に対する接続制約を追加して辞書を返す
		return self.map_append2constraints(D, appendix)

if __name__ == '__main__':

	## 追加機能表現・追加接続制約の取得
	aec = AdditionalEntryCollector(
		'../../data/JFEcorpus_ver2.1',
		'../ttj_dict.kch') ## ttj_dict.kch はheadに変換された辞書
	F, C = aec.get_add_entry()

	for f in F:
		print f

	## 機能表現辞書の構築
	if False:
		dc = DictCompiler()
		#dc.build_ttj('test_db.kch', '../../src/ttj11core2seq')
		FE = dc.extended_dict('../../src/ttj11core2seq', F)
		for k, v in FE.iteritems():
			print k + '\t' + '/'.join(v)

	## 接続制約辞書の構築
	if False:
		cc = ConstraintCompiler(
			'../../src/connectID.txt',
			'../../src/fe_right_left_rule_list.txt')
		D = cc.get_dictionary(C)
		for k, v in D.iteritems():
			print k + '\t' + ';'.join(v)





