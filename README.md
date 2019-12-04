# 仮想フォルダ生成システム
本システムは，計算機内のワーキングディレクトリを分類し，仮想フォルダとして提示する．
+ `CFAL` により履歴収集
  + http://github.com/Ryota0312/CFAL
  
## Requirements
+ Python 3.x
  
## インストール
### Use Pipenv(推奨)
+ `$ git clone git@github.com:Ryota0312/VFGen.git`
+ `$ cd VFGen`
+ `$ pipenv install`

+ ※ how to get pipenv(example)
  + `sudo pip3 install pipenv`

### システムにインストール
+ `$ git clone git@github.com:Ryota0312/VFGen.git`
+ `$ cd VFGen`
+ `$ pip install -r requirements.txt`

## 設定
+ `settings.yml` で設定．
  + `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所(絶対パス)
  + `VIRTUAL_FOLDER_PATH` : 仮想フォルダ生成先(絶対パス)
  + `VIRTUAL_FOLDER_NAME` : 仮想フォルダの名前． `VIRTUAL_FOLDER_PATH/VIRTUAL_FOLDER_NAME` に各仮想フォルダが生成される．
	+ `CLUSTERING` : 作業内容別仮想フォルダの名前を設定
	+ `USED` : 使用時期別仮想フォルダの名前を設定
	+ `RECENT` : 最近使用したワーキングディレクトリの仮想フォルダの名前を設定
  + `DB_PATH` : ワーキングディレクトリのデータベース(絶対パス)
  + `WD_DISCOVER_SETTINGS` : ワーキングディレクトリ推定に関する設定
	+ `weight` : 階層の深さによる重み．例) [7,5,3,1] は，1-2層目が7，2-3層目が5...4層目以降は1
	+ `threshold` : 分割の閾値
  + `CLUSTERING_SETTINGS` : クラスタリングに関する設定
	+ `pca_nconponents` : 主成分分析による次元圧縮の次元数
	+ `div_threshold` : 階層的クラスタリングによるデンドログラムを分割する閾値
	+ `save_dendrogram` : クラスタリング時にデンドログラムを保存するかどうか（True/False）
  + `CFAL_SETTINGS` : CFALの設定
	+ `HOME_DIRECTORY` : ホームディレクトリを設定
	+ `IGNORE_LIST` : 監視対象から除外するファイルを正規表現で指定する．複数指定可能．
  
## 実行
### CFALの起動
+ 起動
  1. `$ pipenv run subaru cfal --init`
  2. `$ pipenv run subaru cfal --start`
+ 停止
  1. `$ pipenv run subaru cfal --stop`

### 仮想フォルダの生成
1. `$ pipenv run subaru update`
2. `$ pipenv run subaru create`

or

1. `$ python bin/subaru.py update`
2. `$ python bin/subaru.py create`

## 生成される仮想フォルダ
+ 使用時期
  + `RECENT` : 直近3週間で使用したワーキングディレクトリ
  + `USED/YYYY/MM` : YYYY年のサブフォルダにMM月に使用したワーキングディレクトリが分類される
+ 作業内容
  + `CLUSTERING` : Task0〜にクラスタリング結果が提示される
