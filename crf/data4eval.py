# -*- coding: utf-8 -*-

"""交差検定の出力から評価用の統合データを作成する．"""

import argparse
import os

def gs_iter(annotated_corpus_dir):
    """正解ラベルを取得する関数．"""
    for src in [f for f in sorted(os.listdir(annotated_corpus_dir)) if f != '.DS_Store']:
        for line in open(annotated_corpus_dir + src):
            if not line.startswith(('#','*','EOS')):
                yield (src, line.strip('\n'))

def make_data4eval(annotated_corpus_dir, tagged_dir, otherwise=False):
    """全ての意味ラベルをマージする関数．
    機能表現以外に対してもマージを行う．"""

    gs = gs_iter(annotated_corpus_dir)

    for i in xrange(10):
        for line in open(tagged_dir + '{}.t'.format(i)):
            line = line.strip('\n')
            if line:
                g = gs.next()

                if not otherwise:
                    while not g[1].startswith(('B', 'I')):
                        g = gs.next()

                print '{}\t{}'.format(g[1].split('\t')[0], line.split('\t')[1])
            else:
                print

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus')
    parser.add_argument('tagged')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    make_data4eval(args.corpus, args.tagged)
