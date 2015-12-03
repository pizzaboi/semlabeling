#! /usr/bin/python
#-*- coding: utf-8 -*-

import os

corpus = '../data/JFEcorpus_ver2.1/'

def merge():
    "出力ラベル＋正解ラベル＋形態素素性を出力する"
    L = [line.strip('\n').split('\t')[1] for line in open('rulebased_ver2.1.eval') if not line=='\n']

    for src in [f for f in os.listdir(corpus) if f != '.DS_Store']:
        print src
        for line in open(corpus + src):
            if line.startswith(('#','*')):
                continue
            elif line.startswith('EOS'):
                print
            else:
                print L.pop(0) + '\t' + line.strip('\n')


if __name__ == '__main__':
    merge()
