# 仮想フォルダ生成システム
+ プロトタイプ
+ スクリプト名などが雑なので要修正
+ `CFAL` により履歴収集
  + http://github.com/Ryota0312/CFAL
  
## インストール
+ `$ git clone`
+ `$ python -m venv env`
+ `$ . env/bin/activate`
+ `$ pip install -r requirements.txt`
+ `$ deactivate`

## 設定
+ `$ echo "PATH, ACTIVE_TIME" > db/wds.csv`
+ `settings.yml` で設定．
  + `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所(絶対パス)
  + `DST` : 仮想フォルダ生成先(絶対パス)
  + `SRC` : ワーキングディレクトリのデータベース(絶対パス)
  + `prev_date` : 前回WD推定を行った日時を記録．初期は履歴収集以前の古い日時を設定しておく．
  
## 実行
1. `$ ./vfgen update-wd`
2. `$ ./vfgen create`
3. `$ ./vfgen clustering # beta`

## 各スクリプトの説明
+ `bin/update-wd`
  ワーキングディレクトリを推定して，データベースに保存．
  
+ `bin/create`
  仮想フォルダの生成（使用時期）
  
+ `bin/clustering`
  仮想フォルダの生成（作業内容）
