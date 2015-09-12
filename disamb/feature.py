# -*- coding: utf-8 -*-

import os
import sys

"""SVMのための素性抽出スクリプト

コーパス中の機能表現のそれぞれについて素性を抽出する．コーパスは，１ファイル１文のCaboCha形
式を想定する．各文を機能表現オブジェクトのリストに変換し，文内の機能表現について，テンプレート
で記述される素性を抽出する．各素性は，素性名を整数に変換し，その値を実数（現時点では全て1.0）
に変換する．先頭に意味ラベル，以降に各素性をスペース区切りで出力する．

使用例
	python feature.py > [result_file]
"""

## 機能表現クラス：非機能表現にもこのクラスを使う
class FunctionalExpression:
    """機能表現クラス．

    CaboCha形式の係り受け解析結果から機能表現オブジェクトを作成．
    非機能表現に対してもこのクラスを使用する．

    Attributes
    tag      : X-SEM形式の意味ラベル
    __surface: 形態素表層形, type=list
    features : 形態素素性, type=list
    ctag     : チャンクタグ(B, I, O)
    stag     : 意味タグ(否定, 推量他)
    """
    def __init__(self, line):
        line = line.strip("\n").split("\t")
        self.tag = line[0]
        self.__surface = [line[1]]
        self.features = line[2].split(",")
        self.ctag = ""
        self.stag = ""

        ## X, SEMタグを設定
        if self.tag.startswith("B"):
            self.ctag, self.stag = self.tag.split("-", 1)
        else:
            ## チャンクタグCはチャンクタグOに統合．
            self.ctag = self.tag.replace("C", "O")

    def is_fe(self):
        """is_fe() -> bool

        is_fe is True <=> FunctionalExpression is FE."""
        if self.ctag.startswith("B"):
            return True
        return False

    def update_feature(self, line):
        """形態素素性を更新する関数．

        複数語から構成される機能表現の場合，後続の形態素を順にこの関数に適用することで，
        適切なCaboCha形式に変換する．表層形は，形態素リストとして保持．品詞は機能表現とし，
        品詞細分類1に意味ラベルを割り当てる．品詞細分類2・3は暫定的に*とする．活用型・活用
        形は末尾の形態素を継承する．原形は，更新前の表層に追加する形態素の原形を加える．
        読み・発音は，更新前の素性に追加する形態素の素性を加える．
        """
        f = ["機能表現", self.stag, "*", "*"]
        line = line.strip("\n").split("\t")
        new_features = line[2].split(",")
        f.append(new_features[4])
        f.append(new_features[5])
        f.append(self.surface() + new_features[6])
        f.append(self.features[7] + new_features[7])
        f.append(self.features[8] + new_features[8])
        self.features = f
        self.__surface.append(line[1])

    def surface(self, sep=""):
        """surface() -> string

        機能表現オブジェクトの表層形を返す関数．リストとして保持される機能表現または形態素
        を文字列として返す関数．
        """
        return sep.join(self.__surface)

    ## 書式化
    def __repr__(self):
        return "\t".join((self.stag, self.surface(sep="."), ",".join(self.features)))

def textiter(corpus):
    """textiter() -> string

    コーパス内のファイルを返すジェネレータ．実際なくても良い．インデントを減らすための実装．
    """
    for src in os.listdir(corpus):
        yield src

def apply_template(seq, t, template):
    """apply_template() -> string

    テンプレートを適用し，適切な文字列形式にして返す関数．テンプレートは，素性名とオフセット
    のタプルのリスト．出力は，

    　``素性名[オフセット]|素性名[オフセット]=素性|素性``
    
    の形式の文字列．
    """
    name = "|".join(["%s[%d]" % (f, o) for f, o in template])

    values = []
    for field, offset in template:
        p = t + offset
        if p not in range(len(seq)):
            return None
        values.append(seq[p][field])
    return "%s=%s" % (name, "|".join(values))

def feature(S, cur):
    """素性を抽出する関数．使ってない

    リストS内のcur番目の機能表現オブジェクトから素性を抽出する．"""
    for offset in xrange(-2, 3):
        if cur + offset in xrange(len(S)):
            print "w[%d]:%s" % (offset, S[cur + offset].surface()),
    print
    for offset in xrange(-2, 3):
        if cur + offset in xrange(len(S)):
            print "p[%d]:%s" % (offset, S[cur + offset].features[0]),
    print
    for offset in xrange(-2, 3):
        if cur + offset in xrange(len(S)):
            print "p1[%d]:%s" % (offset, S[cur + offset].features[1]),
    print

if __name__ == "__main__":

    ## 曖昧性情報の辞書化
    #D = {}
    #for line in open("disamb/feambiguity.txt"):
    #    line = line.strip("\n").split("\t")
    #    D[line[0]] = int(line[1])

    ## 素性テンプレート
    templates = []
    #templates += [(("w", i),) for i in range(-2, 3)]
    templates += [(("w", 0),)]
    templates += [(("p", i),) for i in range(-2, 3)]

    corpus = "data/JFEcorpus_ver2.1/"
    feature_id = {}
    counter = -1
    for src in textiter(corpus):

        ## 文のクラス化
        S = []
        for line in open(corpus + src):
            if line.startswith(("#", "*", "EOS")):
                continue
            elif line.startswith(("C", "O", "B")):
                S.append(FunctionalExpression(line))
            elif line.startswith("I"):
                ## 順番に注意：表層より先に素性を更新すること
                S[-1].update_feature(line)

        ## 各形態素から素性を抽出
        seq = [] # 素性リスト
        #F   = [] # 機能表現インデックス
        for i, morph in enumerate(S):
            v = {}
            v["w"] = morph.surface()
            v["p"] = morph.features[0]
            v["p1"] = morph.features[1]
            v["p2"] = morph.features[2]
            v["p3"] = morph.features[3]
            v["ct"] = morph.features[4]
            v["cf"] = morph.features[5]
            v["bf"] = morph.features[6]
            v["rd"] = morph.features[7]
            seq.append(v)

            ## 曖昧性のある機能表現のインデックスを作成
            #if morph.is_fe() and D[morph.surface(sep=".")] > 1:
            #    F.append(i)
            #F = range(len(S))

        ## 素性の抽出
        for i in xrange(len(S)): # ここは冗長
            if S[i].is_fe():
                sys.stdout.write(S[i].stag.strip()) # 正解ラベル
                for template in templates:
                    attr = apply_template(seq, i, template)
                    if attr is not None:
                        if not attr in feature_id:
                            counter += 1
                            feature_id[attr] = counter
                        sys.stdout.write(" %s:1.0" % feature_id[attr])
                print
            else: # 機能表現意外は無視
                pass











