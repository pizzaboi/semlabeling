#-*- coding: utf-8 -*-

"""FE tagger (Longest match principle)

辞書ベースの最長一致法による機能表現タガー．
機能表現解析のベースライン．

Usage:
    python rulebased2.py
"""

## 機能表現タグ
__LABEL_ver2_1__ = set(['判断','否定','疑問','推量-不確実','推量-高確実性',
    '否定推量','意志','願望','当為','不可避','依頼','勧誘','勧め','許可','不許可',
    '不必要','無意味','可能','不可能','困難','容易','自然発生','自発','無意志',
    '試行','伝聞','回想','継続','着継続','発継続','最中','傾向','事前','完了',
    '事後','結果状態','習慣','反復','経歴','方向','授与','受益','受身','使役',
    '付帯-続行','付帯-並行','同時性','継起','終点','相関','対比','添加','比較',
    '場合','順接仮定','順接確定','逆接仮定','逆接確定','理由','目的','並立',
    '例示','様態','比況','程度','強調','感嘆','態度','内容','名詞化','話題'])

import json, codecs
import os

import freq
from morph import Morph

class RulebasedTagger:

    def __init__(self, S):
        self.sentence = S

    def surround_match(self, i, seq):
        """surround_match() --> bool

        i番目以降の形態素表層がseqと一致するかを判定する関数．
        seqはつつじ形式のリスト．ex. ["1:しれ", "2:ない"]
        """
        for token in seq:
            if not token:
                break
            offset = int(token.split(':')[0])
            if not (i + offset) < len(self.sentence):
                return False
            elif self.sentence[i + offset].surface() != token.split(':')[1]:
                return False
        return True

    def comp_rule(self, r1, r2):
        """comp_rule() --> bool

        2つの接続制約情報が一致するかを判定する関数．
        '*'はどの制約とも一致するとする．
        """
        r1 = r1.split(',')
        r2 = r2.split(',')
        for i in xrange(len(r1) - 2):
            if r1[i] != '*' and r1[i] != r2[i]:
                return False
        return True

    def connect_match(self, i, ttj):
        """connect_match() --> bool

        形態素が接続制約を満たすかを判定する関数．
        ttjはつつじIDと表層形の連結．分割後，つつじIDで制約辞書を検索して比較．
        """
        ttj_id, ttj_surface = ttj.split(':')
        ttj_id = ttj_id.replace('.', '')
        if not ttj_id in CR: #slightly faster than .has_key()
            return True
        for rule in CR[ttj_id]:
            if self.comp_rule(rule, self.sentence[i-1].feature()):
                return True
        return False

    def sem_filter_01(self, sec):
        """sem_filter_01() --> str (semantic tag)

        意味カテゴリIDと意味ラベルの連結から意味ラベルを抽出する関数．
        つつじオリジナルのラベルに対していくつかのフィルタを適用する．
        """
        D = {'I1': '推量-不確実' ,
             'I2': '推量-高確実性',
             'I3': '完了', #反実
             'J1': '進行-習慣',
             'J2': '進行-慣習',
             'v1': '付帯-続行',
             'v2': '付帯-並行',
             'w3': '疑問', #感嘆-確認
             'x3': '疑問', #疑問-確認
             'K3': '依頼'}

        data = sec.split(':')
        if data[0][:2] in D:
            return D[data[0][:2]]
        elif data[1] == '無視':
            return '想外'
        else:
            return data[1]

    def sem_filter_02(self, sec):
        if sec == '限定':
            return '程度'
        elif sec in __LABEL_ver2_1__:
            return sec
        else:
            return False

    def set_candidates(self):
        """set_candidates() --> None

        形態素ごとに辞書を検索して，辞書エントリと周辺形態素が一致したとき，機能表現表層と
        意味ラベルを候補に追加する．
        """
        s = self.sentence
        for i in xrange(len(s)):

            # 機能表現の位置を教えるかどうか
            if not s[i].is_fe():
                continue

            #entries = FE.get(s[i].surface())
            if FE.has_key(s[i].surface()):
                entries = FE[s[i].surface()]
            else:
                continue

            #if not entries:
            #    continue

            for entry in entries:
                e = entry.split(',')
                sec, ttj, seq = e[0], e[1], e[2:] # 3sec faster than .pop(0)

                ## 周辺形態素の検証
                if not self.surround_match(i, seq):
                    continue
                #print 'Sequence Matched: %s' % entry

                ## 意味ラベルにフィルタを適用
                sec = self.sem_filter_01(sec)
                sec = self.sem_filter_02(sec)
                if not sec:
                    ## 意味ラベルが不適切な場合は次の形態素へ
                    continue

                ## 接続制約の検証
                if not self.connect_match(i, ttj):
                    #print 'Connection Mismatched: %s' % entry
                    continue

                ## 意味ラベル候補を追加する
                s[i].add_candidate((ttj.split(':')[1], sec))

    def longest_match(self):
        cur = ''
        S = self.sentence
        for i, morph in enumerate(S):
            if not morph.is_tagged(): # タグが未付与のとき
                max_len = 0
                for field in morph.candidates():
                    
                    ttj = field[0].split('.')
                    if len(ttj) >= max_len: # さらに長い表現のとき
                        morph.set_ttjsurface(ttj)

                        if not field[0] in FQ:
                            morph.define_as_begin(field[1])
                        else:
                            morph.define_as_begin(FQ[field[0]])

                        max_len = len(ttj) # 最長更新
                        cur = morph.defined_tag().split('-', 1)[1]

                        ## 2語以上のとき、続く表現も更新する
                        if max_len >= 2:
                            for k, v in enumerate(morph.ttjsurface()):
                                if k != 0:
                                    S[i + k].define_as_inner(field[1])
            else:
                morph.define_as_inner(cur)

    def longest_match_multi(self):
        cur = ''
        S = self.sentence
        for i, morph in enumerate(S):
            if not morph.is_tagged():
                max_len = 0
                for field in set(morph.candidates()):
                    ttj = field[0].split('.')

                    if len(ttj) >= max_len:
                        morph.set_ttjsurface(ttj)
                        if len(ttj) > max_len:
                            morph.define_as_begin(field[1])
                            if len(ttj) >= 2:
                                for k, v in enumerate(morph.ttjsurface()):
                                    if k != 0:
                                        S[i + k].define_as_inner(field[1])
                            max_len = len(ttj)
                        elif len(ttj) == max_len:
                            morph.define_as_multi(field[1])
                            if max_len >= 2:
                                for k, v in enumerate(morph.ttjsurface()):
                                    if k != 0:
                                        S[i + k].define_as_multi(field[1])
                    cur = morph.defined_tag().split("-", 1)[1]
            else:
                morph.define_as_inner(cur)

    ## Run tagger.
    def tagger(self, multi=False):
        self.set_candidates()
        if multi:
            self.longest_match_multi()
        else:
            self.longest_match()
        return self.sentence

## Convert cabocha format to morph sequence.
def encode_sentence(src):
    S = []
    for line in open(src):
        line = line.strip('\n')
        if not line.startswith(('#', '*', 'EOS')):
            S.append(Morph(line))
    return S

def test():
    #srcs = [f for f in os.listdir(args.corpus) if f != '.DS_Store']
    src='../data/JFEcorpus_ver2.1/OC15_00907m_004.depmod'
    S = encode_sentence(src)
    rt = RulebasedTagger(S)
    for morph in rt.tagger(True):
        print repr(morph)
    #rt.print_label()

def main():
    #corpus = '../data/JFEcorpus_ver2.1/'
    #corpus = '700/tmp/'
    corpus = '../data/test300hyphen/'
    for src in [f for f in os.listdir(corpus) if f != '.DS_Store']:
        S = encode_sentence(corpus  + src)
        rt = RulebasedTagger(S)
        res = rt.tagger()
        for morph in res:
            #pass
            print repr(morph)
        print
    #print time.time() - start

if __name__ == '__main__':

    from preprocess import *

    ## 追加機能表現・追加接続制約の取得
    aec = AdditionalEntryCollector(
        '../data/JFEcorpus_ver2.1',
        'ttj_dict.kch')
    F, C = aec.get_add_entry()

    ## 辞書の構築
    dc = DictCompiler()
    FE = dc.extended_dict('../src/ttj11core2seq', F)

    ## 制約の獲得
    cc = ConstraintCompiler(
        '../src/connectID.txt',
        '../src/fe_right_left_rule_list.txt')
    CR = cc.get_dictionary(C)

    ## 頻度情報の取得
    counter = freq.CorpusCounter()
    FQ = counter.frequent_tags("../data/JFEcorpus_ver2.1/")

    #test()
    main()
