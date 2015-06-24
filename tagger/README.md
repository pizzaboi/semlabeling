## Semantic Tagger for Japanese Functional Expressions (FEs)
Assign semantic labels to each FEs in the input sentence.

## Usage
```
$ echo "パソコンが壊れて遅れたわけではない" | bash run_tagger.sh
* 0 1D 0/1 0.464612
O	パソコン	名詞,一般,*,*,*,*,パソコン,パソコン,パソコン
O	が	助詞,格助詞,一般,*,*,*,が,ガ,ガ
* 1 2D 0/1 0.464612
O	壊れ	動詞,自立,*,*,一段,連用形,壊れる,コワレ,コワレ
B-並立	て	助詞,接続助詞,*,*,*,*,て,テ,テ
* 2 -1D 5/5 0.000000
O	遅れ	動詞,自立,*,*,一段,連用形,遅れる,オクレ,オクレ
B-過去	た	助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
B-否定	わけ	名詞,非自立,一般,*,*,*,わけ,ワケ,ワケ
I-否定	で	助動詞,*,*,*,特殊・ダ,連用形,だ,デ,デ
I-否定	は	助詞,係助詞,*,*,*,*,は,ハ,ワ
I-否定	ない	形容詞,自立,*,*,形容詞・アウオ段,基本形,ない,ナイ,ナイ
EOS
```


## Components
- **run_tagger.sh** - Main file.
- **unit_sent_feature.py** - Script for extracting features.
- **output.py** - Script for displaying the result.
- **1627.m** - Model file trained with 1,627 texts in the OC category.
- sentence.cabocha - Artifact (result from cabocha).
- sentence.f - Artifact (features).
- sentence.tagged - Artifact (list of tagged labels).
- README.md - This file.

## Required
- [CaboCha](http://taku910.github.io/cabocha/)
- [CRFSuite](http://www.chokkan.org/software/crfsuite/)
