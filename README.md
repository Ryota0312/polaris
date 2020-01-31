# 仮想フォルダ生成システム
+ 本システムは，計算機内のワーキングディレクトリを分類し，仮想フォルダとして提示する．
+ 仮想フォルダは，ワーキングディレクトリへのシンボリックリンクにより作成される．このため，仮想フォルダ自体を削除しても，元のフォルダへの影響は無い．
+ 本システムでは，以下の3種類の仮想フォルダが生成される．
  + 使用時期
	+ `RECENT` : 直近3週間で使用したワーキングディレクトリ
	+ `USED/YYYY/MM` : YYYY年のサブフォルダにMM月に使用したワーキングディレクトリが分類される
  + 作業内容
	+ `CLUSTERING` : Task0〜にクラスタリング結果が提示される
+ 実装の詳細は，[TECHNICAL-MEMO](/docs/technical_memo.md)に記述する．

## Requirements
+ Python 3.x
+ fswatch
  + https://github.com/emcrisostomo/fswatch
  
## Install fswatch
### Linux
1. `$ sudo apt install fswatch`

aptでインストールできない場合，

1. `$ wget https://github.com/emcrisostomo/fswatch/releases/download/1.14.0/fswatch-1.14.0.tar.gz`
2. `$ tar -zxvf fswatch-1.14.0.tar.gz`
3. `$ cd fswatch-1.14.0`
4. `$ ./configure`
5. `$ make`
6. `$ sudo make install`
7. `$ sudo ldconfig`

### Mac OS X
```
# MacPorts
$ port install fswatch
	
# Homebrew
$ brew install fswatch
```

## インストール
### Use Pipenv(推奨)
+ `$ git clone git@github.com:Ryota0312/polaris.git`
+ `$ cd polaris`
+ `$ pipenv install`

+ ※ how to get pipenv(example)
  + `sudo pip3 install pipenv`

### システムにインストール
+ `$ git clone git@github.com:Ryota0312/polaris.git`
+ `$ cd polaris`
+ `$ pip install -r requirements.txt`

## 設定
+ `settings.yml` で設定．

### 必須項目
+ `PYTHON_PATH` : pythonのパス．`$ which python` の結果．仮想環境を用いている場合 `$ pipenv run which python` など．
+ `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所(絶対パス)
+ `VIRTUAL_FOLDER_PATH` : 仮想フォルダ生成先(絶対パス)
+ `DB_PATH` : ワーキングディレクトリのデータベース(絶対パス)
+ `CFAL_SETTINGS` : CFALの設定
  + `HOME_DIRECTORY` : ホームディレクトリを設定
  + `IGNORE_LIST` : 監視対象から除外するファイルを正規表現で指定する．複数指定可能．

### 任意項目(特に変更がなければsampleと同じでよい項目)
+ `VIRTUAL_FOLDER_NAME` : 仮想フォルダの名前． `VIRTUAL_FOLDER_PATH/VIRTUAL_FOLDER_NAME` に各仮想フォルダが生成される．
  + `CLUSTERING` : 作業内容別仮想フォルダの名前を設定
  + `USED` : 使用時期別仮想フォルダの名前を設定
  + `RECENT` : 最近使用したワーキングディレクトリの仮想フォルダの名前を設定
+ `WD_DISCOVER_SETTINGS` : ワーキングディレクトリ推定に関する設定
  + `weight` : 階層の深さによる重み．例) [7,5,3,1] は，1-2層目が7，2-3層目が5...4層目以降は1
  + `move_threshold` : 分割の閾値
  + `density_threshold` : 機械的なファイル生成とみなすの閾値
+ `CLUSTERING_SETTINGS` : クラスタリングに関する設定
  + `pca_nconponents` : 主成分分析による次元圧縮の次元数
  + `div_threshold` : 階層的クラスタリングによるデンドログラムを分割する閾値
  + `save_dendrogram` : クラスタリング時にデンドログラムを保存するかどうか（True/False）
  
## 実行
### 初回起動時
```
$ pipenv run polaris init
$ pipenv run polaris cfal --init
$ pipenv run polaris cfal --start
$ pipenv run polaris enable
```

### システムの有効化/無効化
+ 有効化
  + `$ pipenv run polaris enable`

+ 無効化
  + `$ pipenv run polaris disable`

### CFALの起動/停止
+ `CFAL`は，元々以下のリポジトリで開発していたが，本システムに統合した．
  + http://github.com/Ryota0312/CFAL
+ 起動
  1. `$ pipenv run polaris cfal --init`
  2. `$ pipenv run polaris cfal --start`
+ 停止
  1. `$ pipenv run polaris cfal --stop`
  
### 仮想フォルダの生成(手動)
1. `$ pipenv run polaris update`
2. `$ pipenv run polaris create`

## トラブルシューティング
## Linux で「inotify_add_watch: デバイスに空き領域がありません」というエラーが出る場合
+ `/proc/sys/fs/inotify/max_user_watches` の値が小さいことが原因で発生している．

1. `$ sudo emacs /etc/sysctl.conf`

2. `fs.inotify.max_user_watches = XXXXXX` を追記．`XXXXXX` はホームディレクトリ以下のファイル数程度が良いはず．

3. `sudo /sbin/sysctl -p`

## ImportError: No module named 'Tkinter'
```
$ sudo apt-get install tk-dev
$ sudo apt-get install python3-tk
```
