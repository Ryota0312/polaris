from lib.AccessLogAnalyzer import *

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer as CV
from sklearn.feature_extraction.text import TfidfTransformer as TFIDF
from sklearn.decomposition import PCA

class Dir2Vec:
    def __init__(self, dirlist, worklist, logs, pca_ncomponents=6):
        self.dirlist = dirlist
        self.worklist = worklist
        self.logs = logs
        self.work_sections = []
        self.ext_pairs = []
        self.vectors = []

        # 各WDの編集を抽出
        self.records = []
        num_of_records = 0
        for d in self.dirlist:
            recs = self.logs.path_filter(d + ".*").op_filter("\ACreated\Z|\AUpdated\Z")
            self.records.append(recs)
            num_of_records += len(recs)
        print("Extracted MODIFY event log")
        print("Records: ",num_of_records)

        self.pca_ncomponents = pca_ncomponents
        self.split_time = 60*30

    def genvec_from_timelines(self, timelines):
        # WDごとにtimelineを取り出し，そのtimelineから隣接拡張子対を作成
        for d in self.dirlist:
            em = np.array([])
            for tl in timelines[d]:
                for i in range(tl[0], tl[1]):
                    ext1 = re.sub(re.compile("[!-/:-@[-`{-~]"), '', self.logs[i].ext)
                    ext2 = re.sub(re.compile("[!-/:-@[-`{-~]"), '', self.logs[i+1].ext)
                    em = np.append(em,ext1+"TO"+ext2)
            self.ext_pairs.append(em)
        # ベクトル化
        for em in self.ext_pairs: self.vectors.append(" ".join(em))
        #cv = CV(min_df=0.1, max_df=0.9)
        cv = CV()
        #tfidf = TFIDF()
        tf = cv.fit_transform(self.vectors)
        #matrix = tfidf.fit_transform(tf).toarray()
        matrix = tf.toarray()
        # ベクトルを正規化
        x = np.array(list(map(np.linalg.norm, matrix)))
        # x = 0となる場合div zeroエラーが発生する．そもそも0ということは，特徴が存在していないためその行を削除する．
        nonzero = (x!=0)
        n_matrix = (matrix[nonzero].T/x[nonzero]).T
        self.dirlist = list(np.array(self.dirlist)[nonzero])
        if self.worklist != None: self.worklist = list(np.array(self.worklist)[nonzero])
        # 主成分分析する
        pca = PCA(n_components=self.pca_ncomponents)
        pca.fit(n_matrix)
        # 分析結果を元にデータセットを主成分に変換する
        transformed = pca.fit_transform(n_matrix)

        return self.dirlist, self.worklist, transformed


    # FIXME:各WDごとのログを使っている．ログ全体のオフセットを用いて行うようにすべき．
    def genvec(self):
        # 30分以上の空きを見つけ作業を区間分割
        if self.work_sections==[]: self.__split_timeline()
        # 区間ごとに集計
        self.__count_extpair()
        # ベクトル化
        for em in self.ext_pairs: self.vectors.append(" ".join(em))
        cv = CV()
        matrix = cv.fit_transform(self.vectors).toarray()
        # ベクトルを正規化
        x = np.array(list(map(np.linalg.norm, matrix)))
        # x = 0となる場合div zeroエラーが発生する．そもそも0ということは，特徴が存在していないためその行を削除する．
        nonzero = (x!=0)
        n_matrix = (matrix[nonzero].T/x[nonzero]).T
        self.dirlist = list(np.array(self.dirlist)[nonzero])
        if self.worklist != None: self.worklist = list(np.array(self.worklist)[nonzero])
        # 主成分分析する
        pca = PCA(n_components=self.pca_ncomponents)
        pca.fit(n_matrix)
        # 分析結果を元にデータセットを主成分に変換する
        transformed = pca.fit_transform(n_matrix)

        return self.dirlist, self.worklist, transformed

    # 区間ごとに集計
    def __count_extpair(self):
        for i in range(len(self.records)):
            em = np.array([])
            for j in range(len(self.records[i])-1):
                if j in self.work_sections[i]: continue
                ext1 = re.sub(re.compile("[!-/:-@[-`{-~]"), '', self.records[i][j].ext)
                ext2 = re.sub(re.compile("[!-/:-@[-`{-~]"), '', self.records[i][j+1].ext)
                em = np.append(em,ext1+"TO"+ext2)
            self.ext_pairs.append(em)
        

    # 30分以上の空きを見つけ作業を区間分割
    def __split_timeline(self):
        for rec in self.records:
            sec = np.array([])
            for i in range(len(rec)-1):
                delta = (rec[i+1].timestamp - rec[i].timestamp).total_seconds()
                if delta >= self.split_time: sec = np.append(sec,i)
            self.work_sections.append(sec)
