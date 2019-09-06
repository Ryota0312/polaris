# 仮想フォルダ生成システム
+ プロトタイプ
+ スクリプト名などが雑なので要修正
+ `CFAL` により履歴収集
  + http://github.com/Ryota0312/CFAL

## 設定
+ `$ echo "PATH, ACTIVE_TIME" > db/wds.csv`
+ `settings.yml` で設定．
  + `ACCESS_LOG_FILE_PATH` : アクセス履歴の場所
  + `DST` : 仮想フォルダ生成先
  + `SRC` : ワーキングディレクトリのデータベース
  + `prev_date` : 前回WD推定を行った日時を記録．初期は履歴収集以前の古い日時を設定しておく．

## 各スクリプトの説明
+ `bin/update-wd`
  ワーキングディレクトリを推定して，データベースに保存．
  
+ `bin/create`
  仮想フォルダの生成（使用時期）
  
+ `bin/clustering`
  仮想フォルダの生成（作業内容）
