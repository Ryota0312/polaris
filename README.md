# 仮想フォルダ生成システム
本システムは，計算機内のワーキングディレクトリを分類し，仮想フォルダとして提示する．
+ `CFAL` により履歴収集
  + http://github.com/Ryota0312/CFAL
  
## インストール
### Use Pipenv(推奨)
+ `$ git clone git@github.com:Ryota0312/VFGen.git`
+ `$ pipenv install`

### システムにインストール
+ `$ git clone git@github.com:Ryota0312/VFGen.git`
+ `$ pip install -r requirements.txt`

## 設定
+ `settings.yml` で設定．
  + `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所(絶対パス)
  + `VIRTUAL_FOLDER_PATH` : 仮想フォルダ生成先(絶対パス)
  + `DB_PATH` : ワーキングディレクトリのデータベース(絶対パス)
  + `WD_DISCOVER_SETTINGS` : ワーキングディレクトリ推定に関する設定
	+ `weight` : 階層の深さによる重み．例) [7,5,3,1] は，1-2層目が7，2-3層目が5...4層目以降は1
	+ `threshold` : 分割の閾値
  + `CLUSTERING_SETTINGS` : クラスタリングに関する設定
	+ `pca_nconponents` : 主成分分析による次元圧縮の次元数
	+ `div_threshold` : 階層的クラスタリングによるデンドログラムを分割する閾値
	+ `save_dendrogram` : クラスタリング時にデンドログラムを保存するかどうか（True/False）
  
## 実行
1. `$ pipenv run update`
2. `$ pipenv run create`

## 各スクリプトの説明
+ `bin/update`
  ワーキングディレクトリを推定して，データベースに保存．ここで，各WDの特徴抽出も行う．
  
+ `bin/create`
  仮想フォルダの生成．
