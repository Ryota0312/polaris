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

@cmd.command(help='Initialize system')
def init():
    with open(app_home + "/scripts/templates/logging.conf.tpl") as ftmp:
        logconf_template = ftmp.read()
        logconf_template = logconf_template.replace("APPLICATION_ROOT", app_home)
        with open(app_home + "/log/logging.conf", "w+") as f:
            f.write(logconf_template)

@cmd.command(help='Collect file access log daemon.')
@click.option('--start', 'cfal_cmd', flag_value='start')
@click.option('--stop', 'cfal_cmd', flag_value='stop')
@click.option('--init', 'cfal_cmd', flag_value='init')
def cfal(cfal_cmd):
    #App logger
    logging.config.fileConfig(app_home + '/log/logging.conf')
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
        ignore_list += '--exclude "' + settings["VIRTUAL_FOLDER_PATH"] + '/.*" '

        with open(app_home + "/scripts/cfal/templates/config.sh.tpl") as ftmp:
            config_template = ftmp.read()
            config_template = config_template.replace("pyreplace_cfal_dir", cfal_dir).replace("pyreplace_home_dir", home_dir).replace("pyreplace_ignore_list", ignore_list)
            with open(app_home + "/scripts/cfal/config.sh", "w+") as f:
                f.write(config_template)

        subprocess.call(app_home + "/scripts/cfal/initialize.sh")
        subprocess.call(["systemctl", "--user", "daemon-reload"])
        logger.info("Initialize CFAL.")
    elif cfal_cmd == "start":
        subprocess.call(app_home + "/scripts/cfal/start.sh")
        logger.info("Start CFAL daemon.")
    elif cfal_cmd == "stop":
        subprocess.call(app_home + "/scripts/cfal/stop.sh")
        logger.info("Stop CFAL daemon.")
    else:
        print("Require 1 cfal option.")
        print("Show help : 'polaris cfal --help'")

@cmd.command(help='Enable polaris system.')
def enable():
    #App logger
    logging.config.fileConfig(app_home + '/log/logging.conf')
    logger = logging.getLogger()

    # 設定ファイルのロード
    try:
        settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
    except:
        print("Error: Cannnot open log file. Check your settings.")
        logger.error("Cannnot open log file. Check your settings.")
        sys.exit()

    with open(app_home + "/scripts/templates/run.sh.tpl") as ftmp:
        run_template = ftmp.read()
        run_template = run_template.replace("APPLICATION_ROOT", app_home).replace("PYTHON_PATH", settings["PYTHON_PATH"])
        with open(app_home + "/scripts/run.sh", "w+") as f:
            f.write(run_template)
    subprocess.call(["chmod", "+x", app_home + "/scripts/run.sh"])

    system_name = str(subprocess.check_output(["uname"], universal_newlines=True)).replace("\n", "")

    if system_name=="Linux":
        with open(app_home + "/scripts/service/polaris.service.tpl") as ftmp:
            service_template = ftmp.read()
            service_template = service_template.replace("APPLICATION_ROOT", app_home)
            with open("/" + "/".join(app_home.split("/")[1:3]) + "/.config/systemd/user/polaris.service", "w+") as f:
                f.write(service_template)
        with open(app_home + "/scripts/service/polaris.timer.tpl") as ftmp:
            timer_template = ftmp.read()
            with open("/" + "/".join(app_home.split("/")[1:3]) + "/.config/systemd/user/polaris.timer", "w+") as f:
                f.write(timer_template)

        subprocess.call(["systemctl", "--user", "daemon-reload"])
        subprocess.call(["systemctl", "--user", "enable", "polaris.timer"])
        subprocess.call(["systemctl", "--user", "start", "polaris.timer"])
    elif system_name=="Darwin":
        with open(app_home + "/scripts/service/polaris.plist.tpl") as ftmp:
            service_template = ftmp.read()
            service_template = service_template.replace("APPLICATION_ROOT", app_home)
            with open("/" + "/".join(app_home.split("/")[1:3]) + "/Library/LaunchAgents/polaris.plist", "w+") as f:
                f.write(service_template)
            subprocess.call(["launchctl", "load", "polaris.plist"])

@cmd.command(help='Disable polaris system.')
def disable():
    system_name = str(subprocess.check_output(["uname"], universal_newlines=True)).replace("\n", "")
    if system_name=="Linux":
        subprocess.call(["systemctl", "--user", "stop", "polaris.timer"])
        subprocess.call(["systemctl", "--user", "disable", "polaris.timer"])
    elif system_name=="Darwin":
        subprocess.call(["launchctl", "unload", "polaris.plist"])

@cmd.command(help='Discovering WD and update DB.')
def update():
    #App logger
    logging.config.fileConfig(app_home + '/log/logging.conf')
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
            logs.load(app_home + "/log.pickle")
            logs.update(logfile)
            logs.dump(app_home + "/log.pickle")
        else:
            logs.parse(logfile)
            logs.dump(app_home + "/log.pickle")
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
    logging.config.fileConfig(app_home + '/log/logging.conf')
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
