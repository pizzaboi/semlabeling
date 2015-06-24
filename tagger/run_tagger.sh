#! /bin/sh

#入力読み込み
read sentence

#
# ここでエラー処理！
#

#CaboCha > 素性抽出 > CRFSuite > 出力
echo ${sentence} | /usr/local/bin/cabocha -f1 > sentence.cabocha
python unit_sent_feature.py < sentence.cabocha > sentence.f
#crfsuite tag -p -m 1627.m < sentence.f > sentence.tagged
/usr/local/bin/crfsuite tag -m 1627.m < sentence.f > sentence.tagged
python output.py
