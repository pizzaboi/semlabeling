#! /usr/bin/python
#-*- coding: utf-8 -*-

"""
機能表現を含まないテキストをリストアップする
機能表現を含まない <=> Bタグを含まない

出力:
no_fes_in_1627.lst
"""

import os

for src in os.listdir('data/JFEcorpus_ver2.1/'):
    for line in open('data/JFEcorpus_ver2.1/' + src):
        if line.startswith('B'):
            break
    else:
        print src
