# semlabeling
機能表現解析用スクリプト群

## コーパス
<img src="https://raw.githubusercontent.com/pizzaboi/semlabeling/master/images/corpus_inst.png" height="300px">

- `diff_files/` - 差分ファイル群(`make_diff.py`の出力)
- `sample_list/` - サンプリングファイル
- `csv2oc.py` - CSV形式のアノテーションデータを１ファイル１文形式のコーパスに変換。
- `make_diff.py` - コーパスとBCCWJとの差分ファイルを作成。

## 辞書ベース解析
- TBA

## CRFによる解析
- `cross_validation.py` - 交差検定の実行スクリプト
- `data4eval.py` - 評価用データを作成。
- `feature.py` - 素性抽出スクリプト。
- `split.py`  - 交差検定用にコーパスを分割。
