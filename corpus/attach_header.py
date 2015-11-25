# -*- coding: utf-8 -*-

"""コーパスの形式を変換するスクリプト

入力：
形態素行の先頭に機能表現タグを付与したテキスト
B:推量	かも	助詞,副助詞,*,*,*,*,かも,カモ,カモ

出力：
ヘッダに機能表現系列を付与したテキスト
#FUNCEXP	O,O,C,B:推量,I:推量,...
"""

import argparse
import os
import sys

def convert(src_dir, dst_dir, sep):
	"""convert() --> file

	src_dir以下のファイルを変換してdst_dir以下に出力する．"""
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
		os.system("mkdir %s" % dst)

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


