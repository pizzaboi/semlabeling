#! /usr/bin/python
#-*- coding: utf-8 -*-

"""
ファイル名と本文のタブ区切りを出力
（表層表現で検索する用に作成）
"""

import os

src = 'data/JFEcorpus_ver2.1/'

for file in os.listdir(src):
    S = ''
    for line in open(src + file):
        if line.startswith(('#', '*', 'EOS')):
            continue
        S += line.split('\t')[1]

    if 'てみてください' in S:
        print file + '\t' + S
