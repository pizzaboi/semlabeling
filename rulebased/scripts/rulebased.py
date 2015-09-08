#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import Kyotocabinet
import Mostfreq # コーパスの頻度情報を数える
from Morph import Morph # Morphクラス作成モジュール

__LABEL_ver2_1__ = ('判断','否定','疑問','推量-不確実','推量-高確実性',
'否定推量','意志','願望','当為','不可避','依頼','勧誘','勧め','許可','不許可',
'不必要','無意味','可能','不可能','困難','容易','自然発生','自発','無意志',
'試行','伝聞','回想','継続','着継続','発継続','最中','傾向','事前','完了',
'事後','結果状態','習慣','反復','経歴','方向','授与','受益','受身','使役',
'付帯-続行','付帯-並行','同時性','継起','終点','相関','対比','添加','比較',
'場合','順接仮定','順接確定','逆接仮定','逆接確定','理由','目的','並立',
'例示','様態','比況','程度','強調','感嘆','態度','内容','名詞化','話題')

def sem_filter(label):
    if label == '限定':
        return '程度'
    elif label in __LABEL_ver2_1__:
        return label
    else:
        return False

def getSenseCandidate(C):
    """文中の各形態素について辞書とのマッチングを行い, 一致する項目を列挙する"""
    for i in xrange(0, len(C)): # 先頭形態素からマッチングを行う

        # 機能表現の位置を与える．未知の文を解析するときはオフにする．
        if not C[i].gold.startswith(('B','I')):
            continue

        surface = C[i].surface
        entries = fe_db.get(C[i].surface) # 辞書を検索

        # 該当する辞書エントリがない場合は以下の処理をパス
        if not entries:
            continue

        for info in entries.split('/'):
            seq = info.split(',')
            SEC = seq.pop(0)
            ttjsurface = seq.pop(0)

            # 周辺形態素のマッチング
            for item in seq:
                if not item: continue # 長さが1のときはOK
                num = int(item.split(':')[0])
                # 長さが不一致
                if not i+num in xrange(len(C)):
                    break
                # 形態素が不一致
                elif C[i+num].surface != item.split(':')[1]:
                    break

            # 周辺形態素が全て一致した場合, 接続情報を確認
            else:
                #print info

                # ラベルver2.1 に伴うラベル修正
                s = sem_filter(SEC1(SEC))
                if not s:
                    continue
                #print info

                # ラベルver2.0 のときのフィルタ
                #s = SEC1(SEC)

                # つつじだけで解析する用
                # 何もフィルタしない
                s = SEC.split(':')[1]

                ttjsurface = ttjsurface.split(':')
                connection = rule_db.get(ttjsurface[0].replace('.',''))

                # 接続情報を考えないとき
                #C[i].sense.append((ttjsurface[1], s))

                # 接続情報をチェックする
                if connection:
                    for item in connection.split(';'):
                        if connect_checker( item, ','.join(C[i-1].feature) ):
                            C[i].sense.append((ttjsurface[1], s))
                            break
                    else:
                        pass
                        #print info, connection
                else:
                    C[i].sense.append((ttjsurface[1], s))
    return C

def connect_checker(L1, L2):
    """connect_checker(L1, L2) is True <=> L1 > L2"""
    L1 = L1.split(','); L2 = L2.split(',')
    for i in xrange(len(L1) - 2):
        if L1[i] != '*' and L1[i] != L2[i]: # ひとつでも不一致なら偽
            return False
    return True

def SEC1(str):
    """意味ラベル部分を抽出"""
    data = str.split(':')
    if data[0].startswith('I1'): return '推量-不確実'
    elif data[0].startswith('I2'): return '推量-高確実性'
    elif data[0].startswith('I3'): return '完了' #'反実'
    elif data[0].startswith('J1'): return '進行-習慣'
    elif data[0].startswith('J2'): return '進行-慣習'
    elif data[1] == '無視': return '想外'
    elif data[0].startswith('v1'): return '付帯-続行'
    elif data[0].startswith('v2'): return '付帯-並行'
    elif data[0].startswith('w3'): return '疑問' #'感嘆-確認'
    elif data[0].startswith('x3'): return '疑問' #'疑問-確認'
    elif data[0].startswith('K3'): return '依頼'
    else: return data[1]

def defineSenseLabel(S, D):
    """意味ラベル候補のうち対応する機能表現長が最大となる意味ラベルを選択する"""
    current_label = ''
    for i in xrange(len(S)): # 先頭の形態素から意味ラベルを決定する
        if not S[i].label: # 既に意味ラベルが決定している場合は以下の処理をパス
            l = 0 # 最長の機能表現の長さ
            for field in S[i].sense:

                ttjsurface = field[0].split('.')
                if len(ttjsurface) >= l: # 最長の機能表現なら意味ラベルを更新する
                    S[i].ttjsurface = ttjsurface

                    # 最長の機能表現が複数ある場合, コーパス中の頻度が大きいラベルを選択
                    if not D.has_key(''.join(S[i].ttjsurface)):
                        S[i].label = 'B-' + field[1]
                    else:
                        S[i].label = 'B-' + D[''.join(S[i].ttjsurface)]
                    l = len(ttjsurface) # current topを更新
                    current_label = S[i].label.split('-', 1)[1]

                    if l >= 2: # 長さが2以上の場合, 後続形態素に同じ意味ラベルを付与
                        for k, v in enumerate(S[i].ttjsurface):
                            if k != 0:
                                S[i+k].label = 'I-' + field[1]
        else:
            S[i].label = 'I-' + current_label

        # 意味ラベル付与結果を出力
        print '{}\t{}'.format(S[i].gold, S[i].label if S[i].label else 'O')
    print

def defineSenseLabel_multi(S, D):
    """意味ラベル候補のうち対応する機能表現長が最大となる意味ラベルを選択する"""
    i = 0
    while i < len(S) -1:
    #for i in xrange(len(S)): # 先頭の形態素から意味ラベルを決定する

        #if not S[i].label: # 既に意味ラベルが決定している場合は以下の処理をパス
        l = 0 # 最長の機能表現の長さ

        if S[i].label:
            i += 1
            continue

        for field in set(S[i].sense):

            ttjsurface = field[0].split('.')

            if len(ttjsurface) >= l:
                S[i].ttjsurface = ttjsurface

                # これまでより長ければ新規 同じなら追加
                if len(ttjsurface) > l:
                    S[i].label = 'B-' + field[1]
                    if len(ttjsurface) >= 2:
                        for k, v in enumerate(S[i].ttjsurface):
                            if k != 0:
                                S[i+k].label = 'I-' + field[1]
                    l = len(ttjsurface)
                elif len(ttjsurface) == l:
                    S[i].label += ',' + field[1]
                    if l >= 2:
                        for k, v in enumerate(S[i].ttjsurface):
                            if k != 0:
                                S[i+k].label += ',' + field[1]
        i += 1

                #current_label.append(field[1])

                # 頻度を考慮するやつ
                # 最長の機能表現が複数ある場合
                # コーパス中の頻度が大きいラベルを選択
                #if not D.has_key(''.join(S[i].ttjsurface)):
                #    S[i].label = 'B-' + field[1]
                #else:
                #    S[i].label = 'B-' + D[''.join(S[i].ttjsurface)]

                #l = len(ttjsurface) # current topを更新
                #current_label = S[i].label.split('-', 1)[1]

                # 長さが2以上の場合, 後続形態素に同じ意味ラベルを付与
                #if l >= 2:
                #    for k, v in enumerate(S[i].ttjsurface):
                #        if k != 0:
                #            #S[i+k].label = 'I-' + field[1]
                #            if 'I' not in S[i+k].label:
                #                S[i+k].label.append('I')
                #            S[i+k].label.append(field[1])


        #else:
        #    S[i].label = ['I'] + current_label
        #i += 1

        # 意味ラベル付与結果を出力

    for i in xrange(len(S)):
    #    print '{}\t{}\t{}'.format(S[i].surface, S[i].gold,
    #                            ','.join(S[i].label) if S[i].label else 'O')

        system = S[i].label if S[i].label else 'O'
        print '{}\t{}'.format(S[i].gold, system)
        #print '{}\t{}\t{}'.format(S[i].surface, S[i].gold, system)

    print

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', help="corpus")
    parser.add_argument('fe', type=str, help="path to fe dict.")
    parser.add_argument('cr', type=str, help="path to connect rule dict.")
    parser.add_argument('--out', type=str, help="dst of tagged result.")
    args = parser.parse_args()
    return args

def main():
    # コーパス読み込み
    for src in [f for f in os.listdir(args.corpus) if f != '.DS_Store']:
        S = []
        for line in open(args.corpus + src):
            line = line.strip('\n')
            if not line.startswith(('#','*','EOS')):
                S.append( Morph(line) )
                #S.append( Morph('NULL\t'+line) )

        # 最長一致による解析
        defineSenseLabel( getSenseCandidate(S), D)
        #defineSenseLabel_multi( getSenseCandidate(S), D)

def test():
    S = []
    for line in open('../../data/JFEcorpus_ver2.1/OC01_00001m_002.depmod'):
        line = line.strip('\n')
        if not line.startswith(('#','*','EOS')):
            S.append(Morph(line))
    S = getSenseCandidate(S)
    for i in range(len(S)):
        print S[i].surface, ', '.join([x[1] for x in S[i].sense])
    defineSenseLabel_multi(S, D)

if __name__ == '__main__':
    args = parse_args()
    fe_db = Kyotocabinet.read_db(args.fe)
    rule_db = Kyotocabinet.read_db(args.cr)
    D = Mostfreq.ranked_dic()

    #test()
    main()
