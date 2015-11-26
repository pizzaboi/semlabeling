# -*- coding: utf-8 -*-

"""Convert corpus format.

Input file example:
	#EVENT0 4       wr:筆者 非未来  0       叙述    成立    0       0
	#EVENT1 6       wr:筆者 非未来  0       叙述    成立    0       0
	* 0 1D 0/1 1.361176
	O       詰め将棋        名詞,一般,*,*,*,*,詰め将棋,ツメショウギ,ツメショーギ    O
	O       の      助詞,連体化,*,*,*,*,の,ノ,ノ    O
	* 1 2D 0/1 0.000000
	O       本      名詞,一般,*,*,*,*,本,ホン,ホン  O
	O       を      助詞,格助詞,一般,*,*,*,を,ヲ,ヲ O
	* 2 -1D 0/4 0.000000
	C       買っ    動詞,自立,*,*,五段・ワ行促音便,連用タ接続,買う,カッ,カッ        O
	B-着継続        て      助詞,接続助詞,*,*,*,*,て,テ,テ  O
	I-着継続        き      動詞,非自立,*,*,カ変・クル,連用形,くる,キ,キ    O
	I-着継続        まし    助動詞,*,*,*,特殊・マス,連用形,ます,マシ,マシ   O
	B-完了  た      助動詞,*,*,*,特殊・タ,基本形,た,タ,タ   O
	O       。      記号,句点,*,*,*,*,。,。,。      O
	EOS

Output file example:
	#EVENT0 4       wr:筆者 非未来  0       叙述    成立    0       0
	#EVENT1 6       wr:筆者 非未来  0       叙述    成立    0       0
	#FUNCEXP        O,O,O,O,C,B:着継続,I:着継続,I:着継続,B:完了,O
	* 0 1D 0/1 1.361176
	詰め将棋        名詞,一般,*,*,*,*,詰め将棋,ツメショウギ,ツメショーギ    O
	の      助詞,連体化,*,*,*,*,の,ノ,ノ    O
	* 1 2D 0/1 0.000000
	本      名詞,一般,*,*,*,*,本,ホン,ホン  O
	を      助詞,格助詞,一般,*,*,*,を,ヲ,ヲ O
	* 2 -1D 0/4 0.000000
	買っ    動詞,自立,*,*,五段・ワ行促音便,連用タ接続,買う,カッ,カッ        O
	て      助詞,接続助詞,*,*,*,*,て,テ,テ  O
	き      動詞,非自立,*,*,カ変・クル,連用形,くる,キ,キ    O
	まし    助動詞,*,*,*,特殊・マス,連用形,ます,マシ,マシ   O
	た      助動詞,*,*,*,特殊・タ,基本形,た,タ,タ   O
	。      記号,句点,*,*,*,*,。,。,。      O
	EOS

"""

import argparse
import os
import sys

def convert(src_dir, dst_dir, sep):
	"""convert() --> file

	src_dir以下のファイルを変換してdst_dir以下に出力する．sepオプションで機能表現タグの区
	切り文字を指定．sepが指定されない場合は，'-'による区切りを使用．"""
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


