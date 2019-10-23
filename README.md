# 仮想フォルダ生成システム
+ ワーキングディレクトリを推定，分類し，仮想フォルダを生成する．
+ `CFAL` により履歴収集
  + http://github.com/Ryota0312/CFAL
  
## インストール
### Use Pipenv(推奨)
+ `$ git clone`
+ `$ pipenv install`

### システムにインストール
+ `$ git clone`
+ `$ pip install -r requirements.txt`

## 設定
+ `settings.yml` で設定．
  + `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所(絶対パス)
  + `DST` : 仮想フォルダ生成先(絶対パス)
  + `SRC` : ワーキングディレクトリのデータベース(絶対パス)
  + `prev_date` : 前回WD推定を行った日時を記録．初期は"initial"と設定しておく．
  
## 実行
1. `$ pipenv run update`
2. `$ pipenv run create`

## 各スクリプトの説明
+ `bin/update`
  ワーキングディレクトリを推定して，データベースに保存．ここで，各WDの特徴抽出も行う．
  
+ `bin/create`
  仮想フォルダの生成
