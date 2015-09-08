#! /usr/bin/python
# -*- coding: utf-8 -*-

import collections
import json, codecs

## core2seqの各エントリを辞書型にして返す関数．
def ttj2dict(e):
	keys = ["surface", "ttj_id", "sem_id", "sem"]

	e = e.split(",")
	sem_id, sem = e[0].split(":")
	ttj_id, surface = e[1].split(":")
	surface = surface.split(".")

	return dict(zip(keys, [surface, ttj_id, sem_id, sem]))

def build_db():
	ret = collections.defaultdict(dict)

	## core2seq を追加
	for line in open("src/ttj11core2seq"):
		entries = line.strip("\n").split("\t")[1]
		for e in entries.split("/"):
			D = ttj2dict(e)
			head = D["surface"][0]
			key = "".join(D["surface"]) 
			ret[head][key] = D

	## 新規エントリを追加
	for line in open("rulebased/fe_list"):
		if not (line.startswith("#") or line == "\n"):
			D = ttj2dict(line.strip("\n"))
			head = D["surface"][0]
			key = "".join(D["surface"])
			ret[head][key] = D

	return ret

if __name__ == "__main__":
	ret = build_db()
	with codecs.open("rulebased/fe_dict.json", "w", "utf-8") as f:
		json.dump(ret, f, ensure_ascii=False, indent=4)
