#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict
import os
import sys

def readiter(srcs, names=('y','w','info','ne'), sep='\t', no_tag=False):
    """readiter() --> list of dict

    ファイルリストを引数として受け取る．各形態素から基本素性の辞書を作成し、ファイルごとに
    リストにして返す．基本素性は，引数namesとして受け取るが，デフォルトでは機能表現タグ・
    表層形・形態素素性・固有表現タグとする．対象のファイルがアノテーションされていない場合，
    no_tagオプションを指定することで，先頭にunkownを追加し，リスト長を調整する．
    """
    seq = []
    for src in [f for f in srcs if f != '.DS_Store']:
        print src
        for line in open(args.corpusdir + src, 'r'):
            line = line.strip('\n')

            if line.startswith(('#', '*')): continue

            elif line == 'EOS':
                # ファイル単位でイテレート
                yield seq
                seq = []

            else:
                fields = ['unknown'] if no_tag else [] #リスト長の調整
                fields.extend(line.split(sep))
                if len(fields) != len(names):
                    raise ValueError("Invalid line: %s\n" % line)
                seq.append(dict(zip(names, tuple(fields[:3]))))

def apply_template(seq, t, template):
    """apply_template() -> string

    テンプレートを適用し，適切な文字列形式にして返す関数．テンプレートは，素性名とオフセット
    のタプルのリスト．出力は，``素性名[オフセット]|素性名[オフセット]=素性|素性``の形式の
    文字列．
    """
    name = '|'.join(['%s[%d]' % (f, o) for f, o in template])

    values = []
    for field, offset in template:
        p = t + offset
        if p not in range(len(seq)):
            return None
        values.append(seq[p][field])

    return '%s=%s' % (name, '|'.join(values))

## Escape colon for CRFSuite.
def escape(src):
    return src.replace(':','__COLON__')

## Extract features and write down features list.
def extract_feature(src_list, EXTRACT_O=False):
    templates =[]
    ws = 2 # window size

    ## unigram素性
    templates += [(('w',i),) for i in range(-ws, ws+1)]
    templates += [(('p',i),) for i in range(-ws, ws+1)]
    templates += [(('p',i), ('p1',i)) for i in range(-ws, ws+1)]
    templates += [(('p',i),('p1',i),('p2',i)) for i in range(-ws, ws+1)]
    templates += [(('p',i),('p1',i),('p2',i), ('p3',i)) for i in range(-ws, ws+1)]
    templates += [(('cf',i),) for i in range(-ws, ws+1)]
    templates += [(('bf',i),) for i in range(-ws, ws+1)]
    templates += [(('bf',i),('p',i)) for i in range(-ws, ws+1)]
    templates += [(('bf',i),('p',i),('p1',i)) for i in range(-ws, ws+1)]
    templates += [(('bf',i),('p',i),('p1',i),('p2',i)) for i in range(-ws, ws+1)]

    ## bigram素性
    templates += [(('p', i), ('p', i+1)) for i in range(-ws, ws)]
    templates += [(('w', i), ('w', i+1)) for i in range(-ws, ws)]
    templates += [(('bf',i), ('bf',i+1)) for i in range(-ws, ws)]
    templates += [(('cf',i), ('w', i+1)) for i in range(-ws, ws)]

    ## 機能表現辞書
    known = defaultdict(int)
    for fe in open('KnownExpressionList'):
        known[fe.strip('\n')] += 1
    templates += [(('bigram',i),) for i in range(-ws, ws+1)]

    ## Main process (extract features per sentence). 
    for seq in readiter(src_list): #seq={morph1={}, morph2={},...}

        ## Get the features from each morphemes.
        for i in xrange(len(seq)):
            morph_info = seq[i]['info'].split(',')
            seq[i]['p']  = morph_info[0] # 品詞
            seq[i]['p1'] = morph_info[1] # 品詞細分類1
            seq[i]['p2'] = morph_info[2] # 品詞細分類2
            seq[i]['p3'] = morph_info[3] # 品詞細分類3
            seq[i]['ct'] = morph_info[4] # 活用型
            seq[i]['cf'] = morph_info[5] # 活用形
            seq[i]['bf'] = morph_info[6] # 基本形
            seq[i]['rd'] = morph_info[7] if len(morph_info) > 7 else seq[i]['bf'] # 読み
            seq[i]['pr'] = morph_info[8] if len(morph_info) > 7 else seq[i]['bf'] # 発音
            seq[i]['bigram'] = 'False'

        for j in xrange(len(seq) - 1):
            bigram = seq[j]['w'] + seq[j+1]['w']
            seq[j]['bigram'] = str(bigram in known)

        if EXTRACT_O: #機能表現以外からも素性抽出する場合
            for t in range(len(seq)):
                sys.stdout.write(seq[t]['y']) #ラベル出力
                for template in templates: #素性出力
                    attr = apply_template(seq, t, template)
                    if attr is not None:
                        sys.stdout.write('\t%s' % escape(attr))
                print #形態素区切り
            print #文区切り

        else: #機能表現からのみ素性抽出する場合
            for t in range(len(seq)):
                if seq[t]['y'] == 'O': #機能表現以外を無視
                    continue
                elif seq[t]['y'] == 'C': #述部区切り
                    print
                elif seq[t]['y'].startswith(('B','I')): #素性出力
                    sys.stdout.write(seq[t]['y'])
                    for template in templates:
                        attr = apply_template(seq, t, template)
                        if attr is not None:
                            sys.stdout.write('\t%s' % escape(attr))
                    print #形態素区切り

## Parse arguments.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpusdir', type=str, help="corpus directory")
    parser.add_argument('-o', action='store_true', help="extract from O")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    #print '\033[38;5;46m' + str(args) + '\033[0m'
    #srcs = [f.strip('\n') for f in sys.stdin]
    srcs = [f for f in os.listdir(args.corpusdir) if f != '.DS_Store']
    extract_feature(srcs, args.o)
