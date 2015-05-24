#! /usr/bin/python
# -*- coding: utf-8 -*-

## Make data for evaluation.

import argparse
import os

## Merge result from CRFSuite with annotated gold standard.
def make_data4evaluation():

    ## Store all gold-labels into list.
    L = []
    for src in [f for f in os.listdir(args.corpus) if f != '.DS_Store']:
        for line in open(args.corpus + src):
            if not line.startswith(('#','*','EOS')):
                L.append(line.strip('\n'))

    ## Merge with result from CRFSuite.
    for i in xrange(10):
        for line in open(args.tagged + '{}.t'.format(i)):
            line = line.strip('\n')
            if line:
                gold = L.pop(0)

                ## For normal cross-validation (just merge two labels.)
                #fo.write('{}\t{}\n'.format(
                #    gold.split('\t')[0], line.split('\t')[1]))

                ## For FE-only cross-validation (merge only when gold is FE.)
                while not gold.startswith(('B','I')):
                    gold = L.pop(0)
                print '{}\t{}'.format(
                        gold.split('\t')[0], line.split('\t')[1])

                # BIを教えて検定するけどエラー分析ようのファイルをみるとき
                #while not gold.startswith(('B','I')):
                #    gold = L.pop(0)
                #print '\t'.join((gold.split('\t')[1], gold.split('\t')[0], line.split('\t')[1]))

                #print gold.split('\t')[0] + '\t' + line.split('\t')[1]
            else:
                print

## Parse arguments.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus')
    parser.add_argument('tagged')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    make_data4evaluation()
