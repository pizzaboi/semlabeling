#! /usr/bin/python
# -*- coding: utf-8 -*-

## Make data for evaluation.

import argparse
import os

def gs_iter(annotated_corpus_dir):
    """正解ラベルを取得"""
    for src in [f for f in os.listdir(annotated_corpus_dir) if f != '.DS_Store']:
        for line in open(annotated_corpus_dir + src):
            if not line.startswith(('#','*','EOS')):
                yield (src, line.strip('\n'))

## Merge result from CRFSuite with annotated gold standard regardless of semantic tags.
def make_data4evaluation(annotated_corpus_dir, tagged_dir):

    gs = gs_iter(annotated_corpus_dir)

    for i in xrange(10):
        for line in open(tagged_dir + '{}.t'.format(i)):
            line = line.strip('\n')
            if line:
                g = gs.next()
                print '{}\t{}'.format(g[1].split('\t')[0], line.split('\t')[1])
            else:
                print

## Merge result from CRFSuite with annotated gold standard only if FE.
def make_data4evaluation_only_fe(annotated_corpus_dir, tagged_dir):
    """正解(\t)出力 を作成する"""

    ## get generator for gold standards.
    gs = gs_iter(annotated_corpus_dir)
    
    ## merge gold standards with output from CRFSuite.
    for i in xrange(10):
        for line in open(tagged_dir + '{}.t'.format(i)):
            line = line.strip('\n')
            if line:

                ## get gold standards only from functional expressions.
                g = gs.next()
                while not g[1].startswith(('B','I')):
                    g = gs.next()
                print '{}\t{}'.format(g[1].split('\t')[0], line.split('\t')[1])
            else:
                print # separator

## Parse arguments.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus')
    parser.add_argument('tagged')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    make_data4evaluation_only_fe(args.corpus, args.tagged)
