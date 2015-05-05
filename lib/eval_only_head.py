#! /usr/bin/python
# -*- coding: utf-8 -*-

import collections
import sys

def evaluate():
    D = collections.defaultdict(lambda : collections.defaultdict(int))
    P = {'gold':[], 'system':[]}
    R = {'gold':[], 'system':[]}
    #
    # D[意味][p_unit] : precision 出現数
    # D[意味][p_correct] : precision 正解数
    #
    for line in sys.stdin:
        line = line.strip('\n')
        if line.startswith('O'):
            continue

        if not line: #文末での処理

            if P['system']: #precision
                sem = P['system'][0].split('-')[-1]
                D[sem]['p_unit'] += 1
                if P['gold'] == P['system']:
                    D[sem]['p_correct'] += 1
            if R['gold']: #recall
                sem = R['gold'][0].split('-')[-1]
                D[sem]['r_unit'] += 1
                if R['gold'] == R['system']:
                    D[sem]['r_correct'] += 1
            P['gold'], P['system'], R['gold'], R['system'] = [], [], [], []

        else:
            line = line.split('\t'); x, y = line[0], line[1] #x=正解, y=出力
            if y.startswith('B'): #precision
                P['gold'], P['system'] = [x], [y]

            if y.startswith('I'):
                P['gold'].append(x); P['system'].append(y)

            if x.startswith('B'): #recall
                R['gold'], R['system'] = [x], [y]

            if x.startswith('I'):
                R['gold'].append(x); R['system'].append(y)

    p = float(sum([D[k]['p_correct'] for k in D.keys()]))
    tp_fp = float(sum([D[k]['p_unit'] for k in D.keys()]))
    r = float(sum([D[k]['r_correct'] for k in D.keys()]))
    tp_tn = float(sum([D[k]['r_unit'] for k in D.keys()]))

    # 全体の精度出力
    pre = p / tp_fp * 100
    rec = r / tp_tn * 100
    fb1 = 2 * pre * rec / (pre + rec)
    print '\033[38;5;46m'
    print 'precision: %2.2f(%4d/%4d); recall: %2.2f(%4d/%4d); FB1: %2.2f' % (
            pre, p, tp_fp, rec, r, tp_tn, fb1)

    # ラベルごとの精度出力
    for k in sorted(D.keys(), key=lambda x: D[x]['r_unit'], reverse=True):
        if D[k]['p_unit'] == 0 or D[k]['r_unit'] == 3: continue
        pre = float(D[k]['p_correct']) / float(D[k]['p_unit']) * 100
        rec = float(D[k]['r_correct']) / float(D[k]['r_unit']) * 100 if D[k]['r_unit']!=0 else 0.0
        fb1 = 2 * pre * rec / (pre + rec) if pre!=0.0 and rec!=0.0 else 0.0
        print '\t%s   ' % k,
        print '\tpre: %2.2f(%3d/%3d); rec: %2.2f(%3d/%3d); FB1: %2.2f' % (
            pre, D[k]['p_correct'], D[k]['p_unit'],
            rec, D[k]['r_correct'], D[k]['r_unit'], fb1)
    print '\033[0m'

    # チャンキングの精度
    #pre = 0.0; rec = 0.0
    #for k in D.keys():
    #    p += float(sum(D[k]['p_correct']))
    #    pre += float(sum(D[k]['p_correct'].values())) / sum(D[k]['p_unit'].values()) * 100
    #    rec += float(sum(D[k]['r_correct'].values())) / sum(D[k]['r_unit'].values()) * 100
    #print pre, rec

if __name__ == '__main__':
    evaluate()
