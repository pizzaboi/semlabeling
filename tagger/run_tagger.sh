#! /bin/sh

## USAGE:
## echo "入力文" | bash run_tagger.sh

## 入力文読み込み
read sentence

# (エラー処理が入る予定)

## CaboCha解析 > sentence.cabocha
echo ${sentence} | /usr/local/bin/cabocha -f1 > sentence.cabocha

## 素性抽出 > sentence.f
python unit_sent_feature.py < sentence.cabocha > sentence.f

## CRFSuiteによるタグ付与 > sentence.tagged
#crfsuite tag -p -m 1627.m < sentence.f > sentence.tagged
/usr/local/bin/crfsuite tag -m 1627.m < sentence.f > sentence.tagged

## CaboCha解析結果と併せて出力
python output.py
