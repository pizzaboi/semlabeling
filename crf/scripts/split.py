# -*- coding: utf-8 -*-

import argparse
import os

def split(directory, N=10):
    """ディレクトリ内のファイルをN等分する関数．"""
    seq = sorted(os.listdir(directory))
    size = len(seq) / N
    unit = [size] * N
    remain = len(seq) - size * N
    for i in range(remain):
        unit[i] += 1
    return [seq[sum(unit[:i]):sum(unit[:i])+unit[i]] for i in xrange(len(unit))]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='target directory.')
    parser.add_argument('dst', help='destination directory.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    for i, seq in enumerate(split(args.dir)):
        fo = open('%sdataset/%d' % (args.dst, i), 'w')
        for f in seq:
            fo.write(f+'\n')
