#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
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
        for line in open(args.corpusdir + src, 'r'):
            line = line.strip('\n')

            if line.startswith(('#', '*')): continue

            elif line == 'EOS': # ファイル単位でイテレート
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

    arguments:
    seq     : 機能表現素性列
    t       : 対象形態素のインデックス
    template: 素性テンプレート
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

    ## Unigram features.
    templates += [(('w',i),) for i in range(-2, 3)] # *
    templates += [(('p',i),) for i in range(-2, 3)] # *
    templates += [(('p',i), ('p1',i)) for i in range(-2, 3)] # *
    #templates += [(('p1',i),) for i in range(-2, 3)]
    templates += [(('p',i),('p1',i),('p2',i)) for i in range(-2, 3)] # *
    #templates += [(('p2',i),) for i in range(-2, 3)]
    templates += [(('p',i),('p1',i),('p2',i), ('p3',i)) for i in range(-2, 3)] # *
    #templates += [(('p3',i),) for i in range(-2, 3)]
    #templates += [(('ct',i),) for i in range(-2, 3)]
    #templates += [(('cf',i),) for i in range(-2, 3)]
    templates += [(('bf',i),) for i in range(-2, 3)] # *
    templates += [(('bf',i),('p',i)) for i in range(-2, 3)] # *
    templates += [(('bf',i),('p',i),('p1',i)) for i in range(-2, 3)] # * 78.56%
    templates += [(('bf',i),('p',i),('p1',i),('p2',i)) for i in range(-2, 3)] # * 78.55%
    #templates += [(('rd',i),) for i in range(-2, 3)]
    #templates += [(('pr',i),) for i in range(-2, 3)]


    ## Bigram features.
    templates += [(('p',i), ('p',i+1)) for i in range(-2, 2)] #78.69%
    templates += [(('w',i), ('w',i+1)) for i in range(-2, 2)] #78.86%
    #templates += [(('p',i), ('p1',i), ('p',i+1), ('p1',i+1)) for i in range(-2, 2)] #78.81%
    templates += [(('bf',i), ('bf',i+1)) for i in range(-2, 2)] #79.11%
    #templates += [(('p1',i), ('p1',i+1)) for i in range(-2, 2)]
    #templates += [(('p2',i), ('p2',i+1)) for i in range(-2, 2)]
    #templates += [(('p3',i), ('p3',i+1)) for i in range(-2, 2)]
    #templates += [(('ct',i), ('ct',i+1)) for i in range(-2, 2)]
    #templates += [(('cf',i), ('cf',i+1)) for i in range(-2, 2)]
    #templates += [(('rd',i), ('rd',i+1)) for i in range(-2, 2)]
    #templates += [(('pr',i), ('pr',i+1)) for i in range(-2, 2)]

    ## 3-gram features.
    #templates += [(('w',i), ('w',i+1), ('w',i+2)) for i in range (-2, 1)]
    #templates += [(('p',i), ('pos',i+1), ('pos',i+2)) for i in range(-2, 1)]
    #templates += [(('p1',i), ('p1',i+1), ('p1',i+2)) for i in range(-2, 1)]
    #templates += [(('p2',i), ('p2',i+1), ('p2',i+2)) for i in range(-2, 1)]
    #templates += [(('p3',i), ('p3',i+1), ('p3',i+2)) for i in range(-2, 1)]
    #templates += [(('ct',i), ('ct',i+1), ('ct',i+2)) for i in range(-2, 1)]
    #templates += [(('cf',i), ('cf',i+1), ('cf',i+2)) for i in range(-2, 1)]
    #templates += [(('bf',i), ('bf',i+1), ('bf',i+2)) for i in range(-2, 1)]
    #templates += [(('rd',i), ('rd',i+1), ('rd',i+2)) for i in range(-2, 1)]
    #templates += [(('pr',i), ('pr',i+1), ('pr',i+2)) for i in range(-2, 1)]

    ## Main process (extract features per sentence). 
    for seq in readiter(src_list, no_tag=True): #seq={morph1={}, morph2={},...}

        ## Get the features from each morphemes.
        for v in seq:
            morph_info = v['info'].split(',')
            v['p'] = morph_info[0]  #pos class
            v['p1'] = morph_info[1] #pos subclass 1
            v['p2'] = morph_info[2] #pos subclass 2
            v['p3'] = morph_info[3] #pos subclass 3
            v['ct'] = morph_info[4] #conjugate type
            v['cf'] = morph_info[5] #conjugate form
            v['bf'] = morph_info[6] #base form
            v['rd'] = morph_info[7] if len(morph_info) > 7 else v['bf'] #read
            v['pr'] = morph_info[8] if len(morph_info) > 7 else v['bf'] #pronunciation

        ## Extract features from all morphemes.
        if EXTRACT_O:
            for t in range(len(seq)):

                ## Output label.
                sys.stdout.write(seq[t]['y'])

                ## Output each features.
                for template in templates:
                    attr = apply_template(seq, t, template)
                    if attr is not None:
                        sys.stdout.write('\t%s' % escape(attr))
                print # blank line as morph separator
            print # blank line as sentence separator

        ## Extract features from only functional expressions.
        else:
            for t in range(len(seq)):

                ## Ignore label O.
                if seq[t]['y'] == 'O':
                    continue

                ## Print blank line as predicate separator.
                elif seq[t]['y'] == 'C':
                    print

                ## Output each features.
                elif seq[t]['y'].startswith(('B','I')):
                    sys.stdout.write(seq[t]['y'])
                    for template in templates:
                        attr = apply_template(seq, t, template)
                        if attr is not None:
                            sys.stdout.write('\t%s' % escape(attr))
                    print # blank line as morph separator

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
