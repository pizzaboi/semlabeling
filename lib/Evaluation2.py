#! /usr/bin/python
# -*- coding: utf-8 -*-

"""機能表現の解析性能評価モジュール
Precision, Recall and F-measure Scorer for Sem-Label tagger

機能表現解析によってラベル付けされた結果からその性能を評価する. 評価尺度には適合率と再現率を用い
る. 評価の際には, BIタグの連続を一単位とみなす.
BIモードでは, 意味ラベルのうちBIタグ部分のみを参照(意味部分を無視)して, 機能表現の範囲同定精度
を評価することができる. また, 述部レベル, 文レベルでの評価も提供する.

入力には, タブ区切り2カラム形式の解析結果を与える. 解析結果は, 1カラム目に正解ラベル, 2カラム目
にシステムによるラベルとし, 文の区切りは改行とする.
"""

__date__ = "6 Aug, 2014"

class Evaluater:
    def __init__(self):
        self.unitcount = 0 # number of units
        self.correctcount = 0 # number of agreement
        self.system = [] # label sequece of system output
        self.gold = [] # label sequence in gold data
        self.value = 0 # calcurated value

    def checker(self):
        """正解データとシステム出力が一致するかどうかを比較し、正解数を数える"""
        if self.system: # 正解データが存在するなら +1
            self.unitcount += 1
        if self.system and self.system == self.gold:
            self.correctcount += 1
        self.system = []
        self.gold = []
    def checker2(self):
        if self.gold:
            self.unitcount += 1
        if self.gold and self.gold == self.system:
            self.correctcount += 1
        self.system = []
        self.gold = []

    def append(self, system, gold):
        """Append labels and make a list of sequence"""
        self.system.append(system)
        self.gold.append(gold)

    def result(self):
        """Calculate Precision or Recall"""
        self.value = float(self.correctcount)/float(self.unitcount) * 100

    def __repr__(self):
        return "{:.2f} ({:4}/{:4}) |".format(
            self.value,
            self.correctcount,
            self.unitcount)

def evaluate_f(src, bi=False):
    Precision = Evaluater()
    Recall = Evaluater()
    for line in open(src):
        line = line.strip('\n')
        if line.startswith('O'):
            continue # Don't care if gold label is 'O'
        if not line:
            Precision.checker()
            Recall.checker()
            #pass
        else:
            line = line.split('\t')
            gold, system = line[0], line[1]
            if bi: # enable bi-only evaluation
                gold, system = gold.split('-')[0], system.split('-')[0]

            # Precision
            if system.startswith('B'):
                Precision.checker2()
                Precision.append(system=system, gold=gold)
            elif system.startswith('I'):
                Precision.append(system=system, gold=gold)
            elif system.startswith(('O','C')): pass
            else: print line + 'HELLO'

            # Recall
            if gold.startswith('B'):
                Recall.checker()
                Recall.append(system=system, gold=gold)
            elif gold.startswith('I'):
                Recall.append(system=system, gold=gold)
            elif gold.startswith(('O','C')): pass
            else: print line

    Precision.result()
    Recall.result()
    F = 2 * Precision.value * Recall.value / (Precision.value + Recall.value)
    print '{} {}  {:.2f}'.format(Precision, Recall, F)
    return Precision, Recall, F

def evaluate_accuracy(src):
    """Calculate accuracy in terms of matrix, sentence."""
    Sentence = Evaluater()
    Matrix = Evaluater()
    before = ''
    for line in open(src):
        line = line.strip('\n')
        if not line:
            Sentence.checker()
        else:
            line = line.split('\t')
            gold, system = line[0], line[1]
            if gold.startswith('B'):
                Sentence.append(system=system, gold=gold)
                if before == 'C' or before == 'O':
                    Matrix.checker()
                Matrix.append(system=system, gold=gold)
            elif gold.startswith('I'):
                Sentence.append(system=system, gold=gold)
                Matrix.append(system=system, gold=gold)
            elif gold.startswith(('O','C')): pass
            else: print gold
            before = gold.split('-')[0]
    Matrix.result()
    Sentence.result()
    print 'MATRIX ACCURACY: {}\nSENTENCE ACCURACY: {}'.format(Matrix, Sentence)

def test(src, description):
    """評価だけを行う場合の処理

    @param src: 評価する解析データのパス
    @param description: データの説明
    """
    delimiter = '-' * 46
    print
    print '\033[38;5;16;48;5;255m{}\033[0m'.format(description)
    #print description
    #print delimiter
    evaluate_f(src, bi=True)
    evaluate_f(src)
    evaluate_accuracy(src)


if __name__ == '__main__':
    test('work/rulebased_ver1.0.eval', 'ラベルver1.0のルールベース解析結果')
    test('work/rulebased_ver2.0.1.eval', 'ラベルver2.0のルールベース解析結果')

    test('work/crf_ver1.0.eval', 'ラベルver1.0のCRF解析結果')
    test('work/crf_ver1.0c.eval', 'ラベルver1.0のCRF解析結果 (述語にラベルを使用)')
    test('work/crf_ver1.0ex.eval', 'ラベルver1.0のCRF解析結果 (素性を拡張)')

    test('work/crf_ver2.0.eval', 'ラベルver2.0のCRF解析結果')
    test('work/crf_ver2.0c.eval', 'ラベルver2.0のCRF解析結果 (述語にラベルを使用)')
    test('work/crf_ver2.0ex.eval', 'ラベルver2.0のCRF解析結果 (素性を拡張)')

    test('work/crf_ver2.0ex-bi.eval', 'ラベルver2.0 機能表現のみで解析')
    test('work/crf_ver2.0ex-bi_2.eval', 'ラベルver2.0 機能表現のみで解析')
    test('work/crf_only_matrix.eval', '文末のみの解析結果')
