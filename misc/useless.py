#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
入力文を MeCab で解析し、内容語のみを抽出
（何用に書いたか忘れた）
"""

import nltk
import MeCab

MECAB_MODE = 'mecabrc'

class Morph:
    def __init__(self, node):
        self.surface = node.surface
        self.pos = node.feature.split(',')[0]
        self.p1 = node.feature.split(',')[1]
        self.p2 = node.feature.split(',')[2]
        self.p3 = node.feature.split(',')[3]

def parse_morphs(text):
    tagger = MeCab.Tagger(MECAB_MODE)
    node = tagger.parseToNode(text)
    S = []
    while node:
        S.append(Morph(node))
        node = node.next
    return S

def bow(passage):
    sentences = passage.split('\n')
    for sentence in sentences:
        BoW = []
        for morph in parse_morphs(sentence):
            if morph.pos in (('名詞', '動詞', '形容詞')):
                BoW.append(morph.surface)
        print '[%s]' % ', '.join(BoW)
        print '[%s]' % ', '.join(BoW)

if __name__ == '__main__':
    bow('ブログ更新しました。\nスーパーガールか沙織さんが光陣だったらなぁ…')
