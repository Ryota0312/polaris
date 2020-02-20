# Technical Memo
## ディレクトリ構成
+ リポジトリ内の各ファイルの説明を述べる．

```
.
├── Pipfile
├── Pipfile.lock
├── README.md
├── bin
│   ├── polaris.py
│   └── reset-db.sh
├── db
│   └── wds.csv
├── docs
│   └── technical_memo.md
├── lib
│   ├── AccessLogAnalyzer.py
│   ├── Clustering.py
│   ├── WDEstimator.py
│   ├── __init__.py
│   ├── csvdb.py
│   └── dir2vec.py
├── log
│   ├── app_log
│   └── logging.conf
├── log.pickle
├── requirements.txt
├── scripts
│   ├── cfal
│   │   ├── access_log
│   │   ├── collect_file_access_log.service
│   │   ├── collect_file_access_log.sh
│   │   ├── config.sh
│   │   ├── error_log
│   │   ├── initialize.sh
│   │   ├── restart.sh
│   │   ├── start.sh
│   │   ├── stop.sh
│   │   └── templates
│   │       ├── collect_file_access_log.plist.tpl
│   │       ├── collect_file_access_log.service.tpl
│   │       ├── collect_file_access_log.sh.tpl
│   │       └── config.sh.tpl
│   ├── run.sh
│   ├── service
│   │   ├── polaris.plist.tpl
│   │   ├── polaris.service.tpl
│   │   └── polaris.timer.tpl
│   ├── templates
│   │   ├── logging.conf.tpl
│   │   └── run.sh.tpl
│   └── uninstall.sh
└── settings.yml.sample
```

+ 主要なディレクトリ/ファイルの一覧を示す．
  + 各ディレクトリの中身は後述．

|通番|ディレクトリ/ファイル名|説明|
|---|---|---|
|1|bin/|本体の `polaris.py` を配置している|
|2|db/|データベース．`wd.csv`というファイルが生成されここに配置される．|
|3|lib/|ライブラリ．|
|4|docs/|本ディレクトリ．ドキュメントを管理するため．|
|5|log/|システムのログとロギング設定ファイルを配置．|
|6|scripts/|シェルスクリプト，systemdの設定ファイルのテンプレート等を配置している．|
|7|Pipfile|pipenvのファイル．パッケージ一覧とPythonのバージョンが書いてある．|
|8|requirements.txt|パッケージ一覧が書いてある．|
|9|settings.yml.sample|settings.ymlのサンプル．|

## bin/
### ファイル一覧
+ `polaris.py`

### `polaris.py`
+ 本体．`python polaris.py enable` のように実行できる．
+ `update`でワーキングディレクトリを推定，`create`で仮想フォルダを生成する．
+ CLIフレームワーク `click` を用いて実装している．このため，各コマンドの処理は，コマンド名に対応するメソッドを参照．
+ コマンド一覧．（`polaris.py --help`，`polaris.py cfal --help`）

```
Usage: polaris.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cfal     Collect file access log daemon.
  create   Create virtual folder.
  disable  Disable polaris system.
  enable   Enable polaris system.
  init     Initialize system
  update   Discovering WD and update DB.
```
```
Usage: polaris.py cfal [OPTIONS]

  Collect file access log daemon.

Options:
  --start
  --stop
  --init
  --help   Show this message and exit.

```

+ `init`
  + 設定ファイルに従って初期設定を行う．
  + 具体的には，`scripts/templates` や `scripts/cfal/templates` のテンプレートファイルから設定ファイル/OSに従ったファイルを生成，配置する．
+ `update`
  + ワーキングディレクトリの推定とクラスタリングのための特徴量抽出を行う．
  + 前回の`update`日時から現在日時までのアクセス履歴を使用する．
  + 上記の結果は `db/wds.csv` に保存される．保存形式は後述するCSV形式．
+ `create`
  + 仮想フォルダを生成する．
  + ここで，データベースの特徴量から特徴ベクトルを作成し，クラスタリングを行う．
  + ワーキングディレクトリへのシンボリックリンクを作成している．
+ `enable`，`disable`
  + systemd/launchd の有効化/無効化を行う．
+ `cfal` : アクセス履歴収集を行うシステム．
  + `init` : 初期設定．設定ファイル/OSに従ってファイルを生成，配置する．
  + `start` : 収集開始．`stop`するまで動き続ける．計算機再起動時は自動起動．
  + `stop` : 収集停止．
  

## `db/`
### ファイル一覧
+ `wds.csv` (システムが生成)

### `wds.csv`
+ 推定されたワーキングディレクトリ，ワーキングディレクトリの使用期間，ワーキングディレクトリの特徴量をCSVで保存．
+ `plaris.py update`によって生成される．
+ 乃村研ミーティング記録書の例を示す．（分かりやすいようにカンマで改行している）
  + 1列目: ワーキングディレクトリの絶対パス
  + 2列目: datetime型のタプルの配列で使用期間を示している．[(s1, e1), (s2, e2)]のように．
  + 3列目: 隣接する拡張子の組．`mdTOmd`はmd→mdを示している．
	+ 拡張子に`TO`という文字列が含まれていれば不具合を起こす可能性あり．

```
/home/ryota/Documents/record/065nom,
[(datetime.datetime(2020, 2, 19, 10, 54, 30), datetime.datetime(2020, 2, 19, 11, 35, 44))],
['mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd', 'mdTOmd']
```


## `lib/`
### ファイル一覧
+ `__init__.py` （これはPythonの使用上必要）
+ `AccessLogAnalyzer.py`
+ `WDEstimator.py`
+ `dir2vec.py`
+ `Clustering.py`
+ `csvdb.py`

### `AccessLogAnalyzer.py`
+ アクセス履歴を扱う．
+ `class AccessLog`
  + 1つの（1行の）アクセス履歴を表すクラス
  + `timestamp`(日時), `file_path`(絶対パス), `operation`(イベント)を持っている．
+ `class AccessLogCollection`
  + `AccessLog`のコレクションクラス
  + `XXX_filter`によりフィルタリングした`AccessLogCollection`クラスを得られる．
+ `class LogParser`
  + CFALによるログファイルをパースするクラス．
  + `parse`でログファイルから`AccessLogCollection`を得る．
  + `dump`, `load`で`pickle`形式で保存，読み込みする．これにより，高速化できる．
  
  

### `WDEstimator.py`
+ ワーキングディレクトリ推定を行う．
+ `class WDEstimator`
  + サンプルコード
	
	```
	# WD推定
	weight = settings['WD_DISCOVER_SETTINGS']['weight']
	move_threshold = settings['WD_DISCOVER_SETTINGS']['move_threshold']
	density_threshold = settings['WD_DISCOVER_SETTINGS']['density_threshold']
	wd = WDEstimator(oneday_rec, weight, move_threshold, density_threshold) # 推定されたワーキングディレクトリを返却
	```
	
### `dir2vec.py`
+ 特徴ベクトルを作成する．
+ `class Dir2Vec`
  + ディレクトリのリストと`AccessLogCollection`を渡すと特徴ベクトルを返却する．
	+ サンプルコード
	
	```
	# 特徴ベクトル作成
	vectorizer = Dir2Vec(list(features.keys()), None, pca_ncomponents=pca_n)
    dirlist, vector = vectorizer.genvec_from_features(list(features.values()))
	```

### `Clustering.py`
+ クラスタリングを行う．
+ `class ClusteringHierarchy`
  + 階層的クラスタリングを行うクラス．
  + `scipy.cluster.hierarchy`を使っている．
  + サンプルコード
	
	```
	#クラスタリング
    ch = ClusterHierarchy(dirlist, vector[:,], None)
    ch.linkage(metric='cosine')
    ch.div(div_threshold)
	cluster = ch.get_cluster()
	```

### `csvdb.py`
+ CSV形式の `wds.csv`　をデータベースとして扱う．
+ 現状は3列という前提になっているので，改良したい．

## `log/`
### ファイル一覧
+ `logging.conf`
+ `app_log`

### `logging.conf`
+ `polaris.py init`で設定ファイルから生成される．（ログの出力先を設定するため）

### `app_log`
+ システムのログ．
+ `update`や`create`を行ったログが記録される．
  + このログを用いて前回の`update`時刻を取得している．

## `scripts/`
### ファイル/ディレクトリ一覧
+ `cfal/`
+ `service/`
+ `templates/`
+ `run.sh`
+ `uninstall.sh`

### `cfal/`
+ ファイルアクセス履歴を収集するシステムCFALのスクリプトを配置したディレクト．
+ `access_log` : アクセス履歴を保存したファイル
  + 時刻，絶対パス，イベント名のCSV形式
+ `error_log` : エラーログ．
+ `config.sh` : CFALの設定．`polaris.py cfal --init`で`cfal/templates/`から生成される．
+ `collect_file_access_log.service` : systemdのサービスファイル
+ `collect_file_access_log.plist` : launchdのサービスファイル

### `service/`
+ polarisのsustemd/launchdのサービスファイルのテンプレートを配置している．これを使って設定ファイルから生成する．

### `templates/`
+ `logging.conf`と`run.sh`のテンプレートを配置している．これを使って設定ファイルから生成する．

### `run.sh`
+ `update`,`create`を実行する．systemd/launchdで`run.sh`を1日1回実行している．

### `uninstall.sh`
+ アンインストール用のファイル．
