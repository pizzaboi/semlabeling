#! /usr/bin/python
# -*- coding: utf-8 -*-

import os

corpus = 'data/JFEcorpus_ver2.1/'
srcs = [f for f in os.listdir(corpus) if f != '.DS_Store']

excepts = []
for src in srcs:
    events = []
    S = []
    for line in open(corpus + src):
        if line.startswith('#'):
            events.append(line.split('\t')[1])
        if not line.startswith(('#','*','EOS')):
            S.append(line.split('\t')[0].split('-',1)[0])

    if not 'B' in S[int(events[-1])+1:]:
        excepts.append(src)

for i in excepts:
    print i
