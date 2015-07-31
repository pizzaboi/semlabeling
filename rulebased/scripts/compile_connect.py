#! /usr/bin/python
# -*- coding: utf-8 -*-

import json, codecs
from collections import defaultdict

class ConnectRuleDictCompiler:
	def __init__(self):
		self.dict = {}

	def expand_origin(self):

		connect = defaultdict(list)
		## 接続情報ID-接続情報 形式のデータを辞書化
		for line in open("src/connectID.txt"):
			fields = line.strip("\n").split("\t")
			connect[fields[0]] = [fields[1]]

		## 接続情報中に別の接続情報IDが含まれている場合，展開する
		for _id, rules in connect.iteritems():
			rules = rules[0].split(";")
			while any(rule.isalnum() for rule in rules):
				expanded = []
				for rule in rules:
					if rule.isalnum():
						expanded.extend(connect[rule])
					else:
						expanded.append(rule)
				rules = expanded

			connect[_id] = rules

		return connect

	def map_ttjid2connect(self):
		## つつじIDから接続情報へマッピング
		connect = self.expand_origin()
		for line in open("src/fe_right_left_rule_list.txt"):
			ttjid, fe, left, right = line.strip("\n").split(",")
			self.dict[ttjid] = connect[left[0:2]]

	def map_append2connect(self, src="rulebased/connect.lst"):
		## 追加表現の接続情報を追加
		for line in open(src):
			_id, rule = line.strip("\n").split("\t")
			self.dict[_id] = rule.split(";")

if __name__ == '__main__':
	compiler = ConnectRuleDictCompiler()
	compiler.map_ttjid2connect()
	compiler.map_append2connect()

	with codecs.open("rulebased/connect.json", "w", "utf-8") as f:
		json.dump(compiler.dict, f, ensure_ascii=False, indent=4)
