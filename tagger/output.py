#! /usr/bin/python
# -*- coding: utf-8 -*-

src_cabocha = 'sentence.cabocha'
src_tagged = 'sentence.tagged'

def get_labels():
    L = []
    for line in open(src_tagged):
        line = line.strip('\n')
        L.append(line)
    return L

def disp(L):
    for line in open(src_cabocha):
        line = line.strip('\n')
        if line.startswith(('#', '*', 'EOS')):
            print line
        else:
            print L.pop(0) + '\t' + line

if __name__ == '__main__':
    L = get_labels()
    disp(L)
