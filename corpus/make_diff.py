# -*- coding: utf-8 -*-

"""
BCCWJと機能表現意味ラベル付与コーパスの差分ファイルを作成するスクリプト

diff file format:
    # S-ID [filename]
    [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
    [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
    ...
    [morph_length]\t[morph_info]\t[ne_tag]\t[sem_tag]
    EOS
morph_length:
  (ex. 2 for 京都)
morph_info: morph-parsed result with IPA dic.
  (ex. 名詞,固有名詞,地域,一般,*,*,京都,キョウト,キョート)
ne_tag: morph-parsed result.
  (ex. B-LOCATION)
sem_tag: annotated semantic tag
  (ex. B-疑問)
"""

import argparse
import os, sys

def header(file_name):
	"""header() -> String. """
	return "# S-ID {}".format(file_name.replace('.depmod', ''))

def morph_boundary(morph):
	"""morph_boundary() -> Int. """
	return len(unicode(morph))

def diff_format(line, sep):
	"""diff_format() -> String. """
	sem_tag, morph, features, ne_tag = line.split('\t')
	sem_tag = sep.join(sem_tag.split('-', 1))
	return '\t'.join(
		(str(morph_boundary(morph)), features, ne_tag, sem_tag))

def main(corpus_dir, srcs, sep):
	for src in srcs:
		f = open(corpus_dir + os.sep + src)

		## ヘッダ出力
		print header(src)

		## 各行を差分形式に変換して出力
		for line in f:
			line = line.strip('\n')
			if line == 'EOS':
				print line
			elif not line.startswith(('#', '*')):
				print diff_format(line, sep)

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--corpus', type=str, default='data/JFEcorpus_ver2.1')
	parser.add_argument('-s', '--sample', type=str, action='append')
	parser.add_argument('--sep', type=str, default='-')
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	args = parse_args()
	corpus = os.path.normpath(args.corpus)

	## コーパスディレクトリの検証
	if not os.path.isdir(corpus):
		sys.stderr.write("Invalid source: %s\n" % corpus)
		sys.exit(0)

	## サンプリングリストから対象のファイルを取得，ソートして実行する
	srcs = []
	for sample in args.sample:
		for line in open(sample):
			srcs.append(line.strip("\n").split('.')[0] + ".depmod")
	main(corpus, sorted(srcs), sep=args.sep)

