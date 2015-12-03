#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

def read_sentence(names=('y','w','info'), sep='\t'):
    seq = []
    for line in sys.stdin:
        line = line.strip('\n')
        if line.startswith(('#', '*')): # ignore non-morph line
            pass
        elif line == 'EOS': # return at EOS
            return seq
        else:
            fields = ['NULL']
            fields += line.split(sep)
            if len(fields) != len(names):
                raise ValueError("Invalid line: %s\n" % line)
            seq.append(dict(zip(names, tuple(fields[:3]))))

## Apply templates, returning a feature in String.
## @pram t: index of current morphme.
def apply_template(seq, t, template):
    name = '|'.join(['%s[%d]' % (f, o) for f, o in template]) #attr name
    values = []
    for field, offset in template: #get attrs
        p = t + offset
        if p not in range(len(seq)):
            return None
        values.append(seq[p][field])
    return '%s=%s' % (name, '|'.join(values))

## escape colon
def escape(src):
    return src.replace(':','__COLON__')

## Extract features
def extract_feature(EXTRACT_O=False):
    templates =[]
    ws = 2

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

    seq = read_sentence()

    for v in seq: #define features
        morph_info = v['info'].split(',')
        v['p'] = morph_info[0] #pos class
        v['p1'] = morph_info[1] #pos subclass 1
        v['p2'] = morph_info[2] #pos subclass 2
        v['p3'] = morph_info[3] #pos subclass 3
        v['ct'] = morph_info[4] #conjugate type
        v['cf'] = morph_info[5] #conjugate form
        v['bf'] = morph_info[6] #base form
        v['rd'] = morph_info[7] if len(morph_info) > 7 else seq[i]['bf']
        v['pr'] = morph_info[8] if len(morph_info) > 7 else seq[i]['bf'] #pronunciation

    ## Extract features regardless of Semantic labels.
    if EXTRACT_O:
        for t in range(len(seq)):
            sys.stdout.write(seq[t]['y']) # output the label
            for template in templates:
                attr = apply_template(seq, t, template)
                if attr is not None:
                    sys.stdout.write('\t%s' % escape(attr)) # output the features
            sys.stdout.write('\n') # morph sep
        sys.stdout.write('\n') # sentence sep

    ## Extract features from only FE sequence with B/I-label
    else:
        for t in range(len(seq)):
            if seq[t]['y'] == 'O': #ignore label O
                continue
            elif seq[t]['y'] == 'C': # predicate sep
                sys.stdout.write('\n')
                #print
            elif seq[t]['y'].startswith(('B','I')): #Extract feature
                sys.stdout.write(seq[t]['y']) # output the label
                for template in templates:
                    attr = apply_template(seq, t, template)
                    if attr is not None:
                        sys.stdout.write('\t%s' % escape(attr)) # output the features
                sys.stdout.write('\n') # morph sep

def parse_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-o','--extract-o', action='store_true',
        help='extract features from O-label.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    extract_feature(True)