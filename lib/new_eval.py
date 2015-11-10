# -*- coding: utf-8 -*-

from collections import defaultdict
import sys

"""
評価用スクリプト

入力：
・タブ区切りの意味ラベルリスト
・空行を文の区切りとする
"""

def eval_reader(file_path):
	"""eval_reader() --> list, list.

	評価用データを一文単位のリストにして返す関数．
	"""
	G, S = [], []
	for line in open(file_path):
		line = line.strip('\n')

		if not line:
			yield G, S
			G, S = [], []
			continue

		gold, system = line.split('\t')
		G.append(gold)
		S.append(system)

def eval_token(file_path):
	"""eval_token() --> None.

	accuracyを計算する関数．"""
	correct, n_token = 0, 0
	for G, S in eval_reader(file_path):
		for i in xrange(len(G) - 1):
			if G[i] == S[i]:
				correct += 1
			n_token += 1
	print "Accuracy"
	print "=" * 60
	print "%.2f (%d/%d)" % (100.0 * correct/n_token, correct, n_token)

def unit_len(seq, index):
	"""unit_len() --> int.

	indexから始まるユニットの長さ(機能表現の長さ)を返す関数．"""
	if not seq[index].startswith('B'):
		return 0
	n = 1
	index += 1
	while index < len(seq) - 1 and seq[index].startswith('I'):
		n += 1
		index += 1
	return n

def eval_chunk(file_path):
	"""eval_chunk() --> None.

	チャンキング性能を計算する関数．
	ユニットの開始点と終了点が一致したときのみ正解とする．
	[B,I,I,I] <--> [B,I,I,I] ==> 一致
	[B,I,I,I] <--> [B,I,I,B] ==> 不一致
	"""
	tp, tp_fn, tp_fp = 0, 0, 0
	for G, S in eval_reader(file_path):
		for i in xrange(len(G) - 1):
			if G[i].startswith('B'):
				tp_fn += 1
				if unit_len(G, i) == unit_len(S, i):
					tp += 1
			if S[i].startswith('B'):
				tp_fp += 1
	precision = 100.0 * tp / tp_fp
	recall = 100.0 * tp / tp_fn
	print "Chunking performance"
	print "=" * 20
	print "Precision: %2.2f (%d / %d)" % (precision, tp, tp_fp)
	print "Recall   : %2.2f (%d / %d)" % (recall, tp, tp_fn)
	print "F1       : %2.2f" % (2 * precision * recall / (precision + recall))

def eval_label(file_path, tex=False):
	"""eval_label() --> None.

	機能表現解析性能を計算する関数．
	ユニットの開始点と終了点が一致し，かつ，意味部分が一致している場合のみ正解とする．
	"""
	D = defaultdict(lambda : defaultdict(int))
	for G, S in eval_reader(file_path):
		for i in xrange(len(G) - 1):
			if G[i].startswith('B'):
				g_tag = G[i].split('-')[-1]
				D[g_tag]['tp_fn'] += 1
				if unit_len(G, i) == unit_len(S, i):
					if g_tag == S[i].split('-')[-1]:
						D[g_tag]['tp'] += 1
			if S[i].startswith('B'):
				s_tag = S[i].split('-')[-1]
				D[s_tag]['tp_fp'] += 1

	macro_tp = sum([D[tag]['tp'] for tag in D])
	macro_tp_fn = sum([D[tag]['tp_fn'] for tag in D])
	macro_tp_fp = sum([D[tag]['tp_fp'] for tag in D])
	macro_pre = 100.0 * macro_tp / macro_tp_fp
	macro_rec = 100.0 * macro_tp / macro_tp_fn
	macro_f1 = 2 * macro_pre * macro_rec / (macro_pre + macro_rec)
	print "FE analysis performance"
	print "=" * 60
	print "Precision: %2.2f (%d/%d)" % (macro_pre, macro_tp, macro_tp_fp),
	print "Recall: %2.2f (%d/%d)" % (macro_rec, macro_tp, macro_tp_fn),
	print "F1: %2.2f" % macro_f1
	print "-" * 60
	if tex:
		print "\\begin{table}[ht]\n\center\\begin{tabular}{l|rr|rr|r}\n\hline"
		for k, v in sorted(D.iteritems(), key=lambda x: x[1], reverse=True):
			precision = 100.0 * v['tp'] / v['tp_fp'] if not v['tp'] == 0 else 0.0
			recall = 100.0 * v['tp'] / v['tp_fn'] if not v['tp'] == 0 else 0.0
			f1 = 2 * precision * recall / (precision + recall) if precision and recall else 0.0
			print "%s & %.2f & (%d/%d) & %.2f & (%d/%d) & %.2f \\\\ \hline" % (
				k,
				precision, v['tp'], v['tp_fp'],
				recall, v['tp'], v['tp_fn'],
				f1)
		print "\\end{tabular}\n\\end{table}"
	else:
		for k, v in sorted(D.iteritems(), key=lambda x: x[1], reverse=True):
			precision = 100.0 * v['tp'] / v['tp_fp'] if not v['tp'] == 0 else 0.0
			recall = 100.0 * v['tp'] / v['tp_fn'] if not v['tp'] == 0 else 0.0
			f1 = 2 * precision * recall / (precision + recall) if precision and recall else 0.0
			print "%12s | %6.2f (%4d/%4d) | %6.2f (%4d/%4d) | %2.2f" % (
				('　　　' + k)[-12:],
				precision, v['tp'], v['tp_fp'],
				recall, v['tp'], v['tp_fn'],
				f1)

if __name__ == '__main__':
	file_path = sys.argv[1]
	if '-a' in sys.argv:
		eval_token(file_path)
	elif '-c' in sys.argv:
		eval_chunk(file_path)
	else:
		eval_label(file_path, tex=True)