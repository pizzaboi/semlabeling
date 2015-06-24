#! /usr/bin/python
# -*- coding: utf-8 -*-

src_cabocha = 'sentence.cabocha' # CaboCha解析結果
src_tagged = 'sentence.tagged' # CRFSuiteの出力

## CRFSuiteの付与結果を読み込み
def get_labels():
    L = [] # 意味ラベルリスト
    for line in open(src_tagged):
        line = line.strip("\n")
        L.append(line)
    return L

## 出力
def disp(L):
    for line in open(src_cabocha):
        line = line.strip("\n")

        ## 形態素行以外はそのまま出力
        if line.startswith(("#", "*", "EOS")):
            print line

        ## 意味ラベル + 形態素行
        else:
            print L.pop(0) + "\t" + line

if __name__ == '__main__':
    L = get_labels()
    disp(L)
