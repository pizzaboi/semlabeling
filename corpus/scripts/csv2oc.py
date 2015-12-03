# -*- coding: utf-8 -*-


"""アノテーション済みCSVからコーパスを構築するスクリプト"""

import argparse
import csv
import os
import sys

class Morph:

    def __init__(self, row):
        self.__filename = row[0].replace('.txt', '.depmod')
        self.__surface = row[1]
        self.__chunk = row[2]
        self.__sem = self.sem_filter(row[3])

    def sem_filter(sem, label):
        """sem_filter() -> string

        ラベル体系の変更に伴うフィルター．
        """
        if label == '確認': return '疑問'
        elif label == '過去': return '完了'
        elif label == '命令': return '依頼'
        elif label == '限定': return '程度'
        else:
            return label        

    def is_inner(self):
        """is_inner() -> boolean"""
        return bool(self.__chunk == 'I')

    def is_predicate(self):
        """is_predicate() -> boolean"""
        return bool(self.__chunk == 'C')

    def is_other(self):
        """is_other() -> boolean"""
        return bool(self.__chunk in ('O', ''))

    def filename(self):
        """filename() -> string"""
        return self.__filename

    def sem(self):
        """sem() -> string"""
        return self.__sem

    def label(self, sep):
        """label() -> string"""
        if self.is_other(): return 'O'
        if self.is_predicate(): return self.__chunk
        return sep.join((self.__chunk, self.__sem))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=str,
        help="csv file annotated with FE tags, utf-8.")
    parser.add_argument('dst', type=str,
        help="destination of corpus.")
    parser.add_argument('-s', '--sep', type=str, default='-',
        help="separator for FE tags.")
    parser.add_argument('-p', '--pre', action='store_true',
        help="assign label C to predicates.")
    parser.add_argument('-m', '--mod', type=str, default='src/team.20130830/OC/',
        help="source data to be annotated.")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    ## 出力先ディレクトリの検証
    dst = os.path.normpath(args.dst) + os.sep
    if not os.path.isdir(dst):
        os.makedirs(dst)

    ## 拡張モダリティタグ付与コーパスの検証
    mod = os.path.normpath(args.mod) + os.sep
    if not mod.endswith('team.20130830/OC/'):
        sys.stderr.write("Invalid source: %s\n" % mod)
        sys.exit(0)

    morphs = []

    reader = csv.reader(open(args.csv, 'U'), delimiter=',')
    try:
        for row in reader:

            ## 空行(=文の区切り)で書き出し
            if not row:
                ## Iタグに意味部分を追記 (I -> I-判断)
                for i in xrange(len(morphs) - 1):
                    if morphs[i].is_inner:
                        morphs[i].__sem = morphs[i-1].sem()

                ## 出力
                fi = open(mod + morphs[0].filename())
                fo = open(dst + morphs[0].filename(), 'w')
                for line in fi:
                    if line.startswith(('#','*','EOS')):
                        fo.write(line)
                        #print line.strip('\n')
                    else:
                        m = morphs.pop(0)
                        fo.write(m.label(args.sep) + '\t' + line)
                        #print m.label(args.sep) + '\t' + line.strip('\n')

                morphs = []

            ## 各行の読み込み
            elif row[0].startswith('OC'):
                morphs.append(Morph(row))

    except csv.Error, e:
        sys.exit("File {}, line {}: {}".format(src, reader, e))
