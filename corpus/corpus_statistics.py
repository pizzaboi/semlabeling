#! /usr/bin/python
# -*- coding: utf-8 -*-

# Show copus statistics
# 
"""
TODO
・コーパス全体の形態素数
・文あたりの形態素数
・機能表現をひとまとまりとして読む
・文節をまたぐ機能表現はどれくらい？（文節内で完結する機能表現はどれくらい？）
・新たに定義したラベルの分布とか

機能表現フォーマット
かもしれない  機能表現,*,*,*,[ないの活用型],[ないの活用形],[最後だけ原形],読み,発音
"""

import collections
import os

__src__ = 'data/JFEcorpus_ver2.1/'
__ignore__ = ('#', '*')


class FunctionalExpression:
    def __init__(self, line):
        fields = line.split('\t')
        features = fields[2].split(',')
        self.surface = fields[1]
        self.morphs = [fields[1]]
        self.p0 = '機能表現' if line.startswith('B') else features[0]
        self.p1 = features[1] if not line.startswith('B') else fields[0].split('-', 1)[1]
        self.p2 = features[2] if not line.startswith('B') else '*'
        self.p3 = features[3] if not line.startswith('B') else '*'
        self.ct = features[4]
        self.cf = features[5]
        self.bs = features[6]
        self.rd = features[7]
        self.pr = features[8]

    def set_as_inner(self, line):
        fields = line.split('\t')
        features = fields[2].split(',')
        self.morphs.append(fields[1])
        self.surface += fields[1]
        self.ct = features[4]
        self.cf = features[5]
        self.bs = ''.join(self.morphs[:-1]) + fields[1]
        self.rd += features[7]
        self.pr += features[8]

    def __str__(self):
        return '\t'.join([
            self.surface,
            ','.join([self.p0, self.p1, self.p2, self.p3, self.ct, self.cf, self.bs, self.rd, self.pr])])

def readiter():
    """形態素クラスのリストを返す"""
    for src in os.listdir(__src__):
        S = []
        for line in open(__src__ + src):
            line = line.strip('\n')
            if line.startswith(__ignore__):
                continue
            elif line.startswith('EOS'):
                yield S
            elif line.startswith('B'):
                S.append(FunctionalExpression(line))
            elif line.startswith('I'):
                S[-1].set_as_inner(line)
            else:
                S.append(FunctionalExpression(line))

class Node:
    def __init__(self, cur, left, right):
        self.cur = [cur]
        self.left = left
        self.right = right

    def __str__(self):
        return ' > '.join((','.join(self.left), ','.join(self.cur), ','.join(self.right)))

def fe_seq():
    for S in readiter():
        seq = []
        for i in xrange(len(S)):
            if S[i].p0 == '機能表現':
                if not seq:
                    seq = [S[i].p1]
                else:
                    seq.append(S[i].p1)
            else:
                if seq:
                    yield seq
                    seq = []

def ordering():
    Freq = collections.defaultdict(int)
    Score = collections.defaultdict(int)
    for seq in fe_seq():
        if len(seq) <= 1:
            continue
        Z = 6.0 / len(seq)
        for index, sem in enumerate(seq):
            pos = index + 1
            Freq[sem] += 1
            Score[sem] += Z * (2 * pos -1) / 2 + 0.5
    for k, v in sorted(Freq.iteritems(), key=lambda x:x[1], reverse=True):
        #print '\t'.join([k, str(v), str(Score[k]/v)])
        print '\t'.join([str(Score[k]/v), str(v), '', k])

def main():
    num_of_sentenece = 0
    num_of_fe = 0
    max_fe = 0
    ave_fe = 0
    min_fe = 99
    pre = collections.defaultdict(int)
    nex = collections.defaultdict(int)
    for S in readiter():
        num_of_sentenece += 1
        for i in xrange(len(S)):
            if S[i].p0 == '機能表現':
                pre[S[i-1].p0] += 1
                if i < len(S) - 1:
                    nex[S[i+1].p0] += 1
                num_of_fe += 1
                max_fe = max(max_fe, len(S[i].morphs))
                ave_fe += len(S[i].morphs)
                min_fe = min(min_fe, len(S[i].morphs))
    print num_of_fe
    print num_of_sentenece
    print ave_fe, max_fe, min_fe
    print 1.0 * ave_fe / num_of_fe
    print '前'
    for k, v in sorted(pre.iteritems(), key=lambda x:x[1], reverse=True):
        print k + '\t' + str(v)
    print '後'
    for k, v in sorted(nex.iteritems(), key=lambda x:x[1], reverse=True):
        print k + '\t' + str(v)

if __name__ == '__main__':
    #main()
    ordering()
