# -*- coding: utf-8 -*-

"""Convert corpus format.

各行の先頭に意味ラベルが付与された形式から，
#FUNCEXP形式に変換するスクリプト．

TODO:
	コロン形式から変換する場合， B:推量:不確実 のようになる可能性がある
	ハイフン形式から変換する場合は問題なし
"""

import argparse
import os
import sys

def convert(src_dir, dst_dir, sep):
	"""convert() --> file

	src_dir以下のファイルを変換してdst_dir以下に出力する．sepオプションで機能表現タグの区
	切り文字を指定．sepが指定されない場合は，':'による区切りを使用．"""
	for src in os.listdir(src_dir):

		## 読み込み
		extmod = []
		cabocha = []
		funcexp = []
		for line in open(src_dir + os.path.sep + src):
			line = line.strip('\n')
			if line.startswith("#EVENT"):
				extmod.append(line)
			elif line.startswith(("* ", "EOS")):
				cabocha.append(line)
			else:
				spl = line.split('\t', 1)
				funcexp.append(spl[0].replace('-',':',1) if sep else spl[0])
				cabocha.append(spl[1])

		## 出力
		fo = open(dst_dir + os.path.sep + src, 'w')
		fo.write(
			'\n'.join(['\n'.join(extmod),
					"#FUNCEXP" + '\t' + ','.join(funcexp),
					'\n'.join(cabocha)])
			 + '\n')

def test_dirs(args):
	src = os.path.normpath(args.src_dir)
	if args.dst:
		dst = os.path.normpath(args.dst)
	else:
		## 指定されていない場合は，JFEcorpus_ver2.1_funcexpのようにする
		dst = src + "_funcexp"
		os.mkdir(dst)

	## ディレクトリかどうかのテスト
	for d in (src, dst):
		if d and not os.path.isdir(d):
			sys.stderr.write("Error: Argument must be directory.\n")
			sys.exit(0)

	return src, dst
	

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('src_dir', type=str,
		help="Original corpus (FE tag at each line.)")
	parser.add_argument('-d', '--dst', type=str,
		help="Destination for the results.")
	parser.add_argument('-s', '--sep', type=str,
		help="Separator for FE tags.")
	args = parser.parse_args()
	return args 

if __name__ == "__main__":
	args = parse_args()

	## ディレクトリのチェック
	src, dst = test_dirs(args)

	## 変換を実行
	convert(src, dst, sep=args.sep)


