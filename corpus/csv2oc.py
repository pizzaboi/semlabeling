#! /usr/bin/ptyhon
# -*- coding: utf-8 -*-

"""
Covert annotated CSV file to BCCWJ-styled corpus.

Supported CSV format:
    FileName,Morphme,ChunkTag,SemanticTag
*FileName must be started with 'OC'.
*ChunkTag must be B, I, C, or blank.
*SemanticTag needed if ChunkTag is B.
*Each file should be separated by blank line.
*CSV file must be written in UTF-8.

Supported CSV sample:
OC09_01707m_002.txt,聞こえ,C,
OC09_01707m_002.txt,て,B,方向
OC09_01707m_002.txt,き,I,
OC09_01707m_002.txt,まし,I,
OC09_01707m_002.txt,た,B,完了
OC09_01707m_002.txt,。,,

OC09_01708m_000.txt,,,,
...

TODO:
dealing tag sequence as dictionary... unstylish!
"""

import argparse
import csv

def convert_csv2oc(src, dst, predicate=False, sep='-'):
    """Convert annotated CSV file to BCCWJ-styled corpus.
    @param src: path to CSV file
    @param dst: path to corpus directory
    @param predicate: discriminate C (predicate) from O (others)
    @param delimiter: label delimiter (ex. B-疑問)"""
    N = 0
    tags = {}
    fname = ''

    reader = csv.reader(open(src, 'U'), delimiter=',')
    try:
        for row in reader:
            if row[0].startswith('OC'):
                #get file name
                fname = row[0].replace('.txt', '.depmod')

                #store semantic tag when chunk tag is B
                if row[2] == 'B':
                    tags[str(N)] = sep.join((row[2], sem_filter(row[3])))
                #get current semantic tag and store it when chunk tag is I
                elif row[2] == 'I':
                    cur = tags[str(N-1)].split(sep, 1)[1]
                    tags[str(N)] = sep.join((row[2],cur))

                #store O-label when no chunk tag annotated
                elif row[2] == 'O' or row[2] == '':
                    tags[str(N)] = 'O'

                #store C-label when chunk tag is C (only if predicate is True)
                elif row[2] == 'C':
                    tags[str(N)] = 'C' if predicate else 'O'
                N += 1

            #output after the blank line
            elif row[0] == '':
                write(dst, fname, tags)
                tags = {}
                N = 0

    except csv.Error, e:
        sys.exit("File {}, line {}: {}".format(src, reader, e))

    #output the last sentence
    write(dst, fname, tags)

def sem_filter(label):
    """Convert ver.2.0 labels to ver.2.1"""
    if label == '確認': return '疑問'
    elif label == '過去': return '完了'
    elif label == '命令': return '依頼'
    elif label == '限定': return '程度'
    else: return label


def write(dir, fname, tags):
    """Output BCCWJ-styled file.
    @param dir: path to corpus directory
    @param fname: output file name
    @param tags: semantic tag sequence"""

    #original text and destination
    #supports only team.20130830/OC/
    fi = open('src/team.20130830/OC/' + fname, 'r')
    fo = open(dir + fname, 'w')

    N = 0
    for line in fi:
        #meta line is output with no change
        if line.startswith(('#','*','EOS')):
            fo.write(line)

        #morpheme line is output with semantic tag prepended
        elif tags.has_key(str(N)):
            fo.write(tags[str(N)] + '\t' + line)
            N += 1

        #there may be no line other than above...
        else:
            fo.write('\t' + line)
            N += 1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('dst', type=str)
    parser.add_argument('--sep', type=str, default="-")
    parser.add_argument('-p','--predicate', action='store_true')
    args = parser.parse_args()
    return args

def check_dst(dir_path):
    """normalize directory path"""
    import os
    #check if dir_path is an existing directory,
    #and create new directory if not.
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    #check if dir_pathi ends with '/'
    if not dir_path.endswith('/'):
        dir_path += '/'

    return dir_path

if __name__ == '__main__':
    args = parse_args()
    convert_csv2oc(
        src=args.src,
        predicate=args.predicate,
        dst=check_dst(args.dst),
        sep=args.sep)
