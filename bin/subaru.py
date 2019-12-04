# -*- coding: utf-8 -*-

import click

import yaml
import os
import datetime
import shutil
import sys
import logging.config
import datetime
import numpy as np
import subprocess
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))
from AccessLogAnalyzer import *
from  WDEstimator import *
from Clustering import *
from dir2vec import *
import csvdb

@click.group()
def cmd():
    pass

@cmd.command(help='Collect file access log daemon.')
@click.option('--start', 'cfal_cmd', flag_value='start')
@click.option('--stop', 'cfal_cmd', flag_value='stop')
@click.option('--init', 'cfal_cmd', flag_value='init')
def cfal(cfal_cmd):
    #App logger
    logging.config.fileConfig(app_home + '/logging.conf')
    logger = logging.getLogger()

    # 設定ファイルのロード
    try:
        settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
    except:
        print("Error: Cannnot open log file. Check your settings.")
        logger.error("Cannnot open log file. Check your settings.")
        sys.exit()

    if cfal_cmd == "init":
        cfal_dir = app_home + "/scripts/cfal"
        home_dir = settings["CFAL_SETTINGS"]["HOME_DIRECTORY"]
        ignore_list = ""
        for ignore in settings["CFAL_SETTINGS"]["IGNORE_LIST"]:
            ignore_list += '--exclude "' + ignore + '" '

        with open(app_home + "/scripts/cfal/templates/config.sh.tpl") as ftmp:
            config_template = ftmp.read()
            config_template = config_template.replace("pyreplace_cfal_dir", cfal_dir).replace("pyreplace_home_dir", home_dir).replace("pyreplace_ignore_list", ignore_list)
            with open(app_home + "/scripts/cfal/config.sh", "w+") as f:
                f.write(config_template)

        subprocess.call(app_home + "/scripts/cfal/initialize.sh")
        logger.info("Initialize CFAL.")
    elif cfal_cmd == "start":
        subprocess.call(app_home + "/scripts/cfal/start.sh")
        logger.info("Start CFAL daemon.")
    elif cfal_cmd == "stop":
        subprocess.call(app_home + "/scripts/cfal/stop.sh")
        logger.info("Stop CFAL daemon.")

@cmd.command(help='Discovering WD and update DB.')
def update():
    #App logger
    logging.config.fileConfig(app_home + '/logging.conf')
    logger = logging.getLogger()

    try:
        settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
    except:
        print("Error: Cannnot open log file. Check your settings.")
        logger.error("Cannnot open log file. Check your settings.")
        sys.exit()

    logfile = settings['ACCESS_LOG_FILE_PATH']
    db = csvdb.Database(settings["DB_PATH"])

    try:
        print("Loading", flush=True)
        logs = LogParser(sep=",")
        if os.path.exists(app_home + "/log.pickle"):
            logs.load()
            logs.update(logfile)
            logs.dump()
        else:
            logs.parse(logfile)
            logs.dump()
        print("Loaded",len(logs.log),"logs")
    except:
        print("Error: Failed to load log dump data. ")
        sys.exit()

    # 前回の更新日時を取得
    prev_date = "initial"
    with open(app_home + "/log/app_log") as f:
        for line in reversed(list(f)):
            if "INFO:Update WD" in line:
                prev_date =  datetime.datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
                break

    if not prev_date == "initial":
        now_date = datetime.datetime.now()
        records = logs.log.op_filter(["Created", "Updated"]).time_filter(prev_date, now_date)
    else:
        now_date = datetime.datetime.now()
        records = logs.log.op_filter(["Created", "Updated"])
    if len(records) == 0: sys.exit(0)

    first = records[0].timestamp
    tail = records[-1].timestamp
    start = datetime.datetime(first.year, first.month, first.day, 0, 0, 0)
    end = datetime.datetime(first.year, first.month, first.day, 23, 59, 59)
    while(True):
        # 1日分
        oneday_rec = records.time_filter(start, end)
        if len(oneday_rec) == 0:
            start += datetime.timedelta(days=1)
            if start > tail: break
            end += datetime.timedelta(days=1)
            continue

        # WD推定
        weight = settings['WD_DISCOVER_SETTINGS']['weight']
        threshold = settings['WD_DISCOVER_SETTINGS']['threshold']
        wd = WDEstimator(oneday_rec, weight, threshold)

        # 特徴抽出
        pca_n = settings['CLUSTERING_SETTINGS']['pca_nconponents']
        vectorizer = Dir2Vec(wd.workingdir, oneday_rec, pca_ncomponents=pca_n)
        features = vectorizer.get_features_from_timelines(wd.timelines_idx)

        # DBへ書き込み
        for d in wd.workingdir:
            tl = db.get(d, 1) + wd.timelines[d]
            ft = db.get(d, 2) + list(features[d])
            db.update(d, str(tl), str(ft))

        logger.info("Update DB use " + str(start) + "to" + str(end) + "accesslog")

        # 1日ずらす
        start += datetime.timedelta(days=1)
        if start > tail: break
        end += datetime.timedelta(days=1)

    # 更新した日時を記録
    logger.info("Update WD")

@cmd.command(help="Create virtual folder.")
def create():
    #App logger
    logging.config.fileConfig(app_home + '/logging.conf')
    logger = logging.getLogger()

    # 設定ファイルのロード
    try:
        settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
    except:
        print("Error: Cannnot open log file. Check your settings.")
        logger.error("Cannnot open log file. Check your settings.")
        sys.exit()

    dst = settings["VIRTUAL_FOLDER_PATH"]
    if not os.path.exists(dst): os.makedirs(dst)

    db = csvdb.Database(settings["DB_PATH"])
    wds = {}
    for i, l in enumerate(db.data):
        wds[l[0]] = eval(l[1])

    ## 使用時期別
    recent_path = dst + "/" + settings["VIRTUAL_FOLDER_NAME"]["RECENT"]
    if os.path.exists(recent_path): shutil.rmtree(recent_path)
    if not os.path.exists(recent_path): os.makedirs(recent_path)
    for m in range(1,13):
        for d in wds.keys():
            if dst in d: continue
            for at in wds[d]:
                # 月別
                if at[0].month <= m and at[1].month >= m:
                    path = dst + "/" + settings["VIRTUAL_FOLDER_NAME"]["USED"] + "/" + str(at[0].year) + "/" + str(m).rjust(2, '0')
                    if not os.path.exists(path): os.makedirs(path)
                    try:
                        if not os.path.exists(path + "/" + d.split("/")[-1]): os.symlink(d, path + "/" + d.split("/")[-1])
                    except:
                        print("Warning:" + path + "/" + d.split("/")[-1] + " cannot make symlink")
                        logger.warning(path + "/" + d.split("/")[-1] + " cannot make symlink")
                # 最近
                if at[0] > (datetime.datetime.now() - datetime.timedelta(days=21)):
                    try:
                        if not os.path.exists(recent_path + "/" + d.split("/")[-1]): os.symlink(d, recent_path + "/" + d.split("/")[-1])
                    except:
                        print("Warning:" + recent_path + "/" + d.split("/")[-1] + " cannot make symlink")
                        logger.warning(recent_path + "/" + d.split("/")[-1] + " cannot make symlink")

    features = {}
    for i, l in enumerate(db.data):
        features[l[0]] = eval(l[2])

    pca_n = settings['CLUSTERING_SETTINGS']['pca_nconponents']    
    vectorizer = Dir2Vec(list(features.keys()), None, pca_ncomponents=pca_n)
    dirlist, vector = vectorizer.genvec_from_features(list(features.values()))

    # クラスタリング
    div_threshold = settings['CLUSTERING_SETTINGS']['div_threshold']
    is_save_dendrogram = settings['CLUSTERING_SETTINGS']['save_dendrogram']
    ch = ClusterHierarchy(dirlist, vector[:,], None)
    ch.linkage(metric='cosine')
    ch.div(div_threshold)
    if is_save_dendrogram: ch.save_dendrogram()

    cluster = ch.get_cluster()

    ## 作業別    
    cluster_path = dst + "/" + settings["VIRTUAL_FOLDER_NAME"]["CLUSTERING"] + "/"
    if os.path.exists(cluster_path): shutil.rmtree(cluster_path)
    if not os.path.exists(cluster_path): os.makedirs(cluster_path)
    for i,c in enumerate(cluster):
        cpath = cluster_path + "/Task" + str(i)
        if not os.path.exists(cpath): os.makedirs(cpath)
        for d in c:
            if not os.path.exists(cpath + "/" + d.split("/")[-1]): os.symlink(d, cpath + "/" + d.split("/")[-1])

    logger.info("Create Virtual Folders")


def main():
    cmd()

if __name__ == '__main__':
    main()
