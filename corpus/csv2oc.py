# -*- coding: utf-8 -*-

import argparse
import csv
import os

## class of line in csv
class Morph:
    def __init__(self, row):
        self.__filename = row[0].replace('.txt', '.depmod')
        self.__surface = row[1]
        self.__chunk = row[2]
        self.__sem = self.sem_filter(row[3])

    ## convert ver.2.0 to ver.2.1
    def sem_filter(sem, label):
        if label == '確認': return '疑問'
        elif label == '過去': return '完了'
        elif label == '命令': return '依頼'
        elif label == '限定': return '程度'
        else:
            return label        

    ## returns True <=> chunk tag is I
    def is_inner(self):
        return bool(self.__chunk == 'I')

    ## returns True <=> chunk tag is C
    def is_predicate(self):
        return bool(self.__chunk == 'C')

    ## returns True <=> chunk tag is O or blank
    def is_other(self):
        return bool(self.__chunk in ('O', ''))

    ## returns source file name
    def filename(self):
        return self.__filename

    ## returns semantic meaning
    def sem(self):
        return self.__sem

    ## returns semantic label
    def label(self, sep):
        if self.is_other(): return 'O'
        if self.is_predicate(): return self.__chunk
        return sep.join((self.__chunk, self.__sem))


## returns parsed arguments in NameSpace object
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('dst', type=str)
    parser.add_argument('-s', '--sep', type=str, default='-')
    parser.add_argument('-p', '--pre', action='store_true')
    args = parser.parse_args()
    return args

## normalize the path to destination directory
def normalize_dst(dst):
    if not dst.endswith('/'):
        dst += '/'
    if not os.path.isdir(dst):
        os.makedirs(dst)
    return dst

if __name__ == '__main__':
    args = parse_args()
    morphs = []

    ## convert csv to bccwj-styled corpus
    reader = csv.reader(open(args.src, 'U'), delimiter=',')
    try:
        for row in reader:
            if not row:
                ## update tags
                for i in xrange(len(morphs) - 1):
                    if morphs[i].is_inner:
                        morphs[i].__sem = morphs[i-1].sem()

                ## output
                fi = open('src/team.20130830/OC/' + morphs[0].filename())
                fo = open(normalize_dst(args.dst) + morphs[0].filename(), 'w')
                for line in fi:
                    if line.startswith(('#','*','EOS')):
                        #fo.write(line)
                        print line.strip('\n')
                    else:
                        m = morphs.pop(0)
                        #fo.write(m.label(args.sep) + '\t' + line)
                        print m.label(args.sep) + '\t' + line.strip('\n')

                morphs = []

            elif row[0].startswith('OC'):
                morphs.append(Morph(row))

    except csv.Error, e:
        sys.exit("File {}, line {}: {}".format(src, reader, e))
