# semlabeling
機能表現解析用スクリプト群

## コーパス
<img src="https://raw.githubusercontent.com/pizzaboi/semlabeling/master/images/corpus_inst.png" height="300px">

- `diff_files/` - 差分ファイル群(`make_diff.py`の出力)
- `sample_list/` - サンプリングファイル
- `csv2oc.py` - CSV形式のアノテーションデータを１ファイル１文形式のコーパスに変換。
- `make_diff.py` - コーパスとBCCWJとの差分ファイルを作成。

## 辞書ベース解析
<img src="https://raw.githubusercontent.com/pizzaboi/semlabeling/master/images/rulebased_inst.png" height="300px">

機能表現辞書を用いた最長一致法による機能表現解析。単語素性に基づく接続制約と、頻度情報にもとづく意味ラベルの選択を行う。

- `preprocess.py`
	- コーパス内の機能表現の獲得
	- 機能表現辞書の構築
	- 接続制約辞書の構築
	- 機能表現一覧の出力
- `freq.py` - コーパス内の機能表現の頻度情報の獲得
- `rulebased2.py` - 機能表現解析の実行

## CRFによる解析
- `cross_validation.py` - 交差検定の実行スクリプト
- `data4eval.py` - 評価用データを作成。
- `feature.py` - 素性抽出スクリプト。
- `split.py`  - 交差検定用にコーパスを分割。
