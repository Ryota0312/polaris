import numpy as np
import datetime
import collections

# ワーキングディレクトリとそれの推定に用いたアクセス履歴断片集合
class WorkingDir:
    def __init__(self, path, logs):
        self.path = path
        self.logs = logs

class WDEstimator:
    def __init__(self, access_log, move_weight, move_threshold):
        self.log = access_log
        self.move_w = move_weight
        self.move_w_const_p = len(move_weight)
        self.move_th = move_threshold
#        print("   Weight:", self.move_w) # 記録用
#        print("Threshold:", self.move_th)# 記録用
        self.timelines = {}
        self.timelines_idx = {}
        # WD 推定
        self.workingdir = self.estimate_wd()

    def estimate_wd(self):
        wds = np.array([])
        interval = np.array([])
        tl = self.__split_with_upper_layer()
#        print("split_with_upper_layer:" + str(len(tl)-1) + "intervals")
        for i in range(1, len(tl)):
            left = tl[i-1]
            #if i != 1: left+=1
            interval = np.append(interval, self.__split_with_cross_mtime(left, tl[i]))
        interval = np.unique(interval)
#        print("split_with_cross_mtime:" + str(len(interval)-1) + "intervals")
        # left = interval[0]からスタート
        # left ~ left+1
        for i in range(1, len(interval)):
            left = int(interval[i-1])
            if i != 1: left+=1
            # 履歴数が少ないタイムラインを無視
            #if interval[i] - left < 5: continue
            # Unmanaged なタイムラインを無視
            if self.__is_unmanaged(left, int(interval[i])): continue
            # タイムラインの最上層共通フォルダをWDとして推定
            est_wd = self.__representative_dir(left, int(interval[i]))
            wds = np.append(wds, est_wd)
            # WDごとにタイムラインを保存
            try:
                self.timelines_idx[est_wd].append((left, int(interval[i])))
                self.timelines[est_wd].append((self.log[left].timestamp, self.log[int(interval[i])].timestamp))
            except:
                self.timelines_idx[est_wd] = [(left, int(interval[i]))]
                self.timelines[est_wd] = [(self.log[left].timestamp, self.log[int(interval[i])].timestamp)]
        # collections.Counter の返り値は (要素, 要素数) のタプル
        return np.array([t[0] for t in collections.Counter(wds).most_common()])

    # WDのタイムラインに含まれるログ数がthreshold以下なら削除
    def pruning(self, threshold):
        boollist = np.array([], bool)
        for d in self.workingdir:
            tl_size = 0
            for tl in self.timelines[d]:
                tl_size += (tl[1] - tl[0])
            if tl_size <= threshold:
                boollist = np.append(boollist, False)
                del self.timelines[d]
            else:
                boollist = np.append(boollist, True)
        self.workingdir = self.workingdir[boollist]
    
    # タイムラインを代表するフォルダ
    def __representative_dir(self, left, right):
        files = []
        for i in range(left, right+1):
            files.append(self.log[i].file_path.split("/")[0:-1])
        mostshort = min(files, key=len)
        for d in range(len(mostshort)-1, 0, -1):
            flag = 1
            for f in range(0, len(files)):
                if files[f][d] != mostshort[d]: flag=0
            if flag==1: return "/".join(mostshort[0:d+1])
                
    # 隣接ファイル間の移動コストでログを分割
    def __split_with_upper_layer(self):
        time_line = [0]
        for i in range(1, len(self.log)-1):
            if self.__move_cost_fixed(self.log[i-1].file_path, self.log[i].file_path) > self.move_th:
                time_line.append(i-1)
        time_line.append(len(self.log)-1)
        return time_line

    # p1 と p2 のパス相違度
    def __move_cost(self, p1, p2):
        p1_list = p1.split("/")
        p2_list = p2.split("/")
        minlen = min(len(p1_list), len(p2_list))
        for i in range(0, minlen):
            if(p1_list[i] != p2_list[i]):
                cost = len(p1_list[i:]) + len(p2_list[i:])
                if i <= self.move_w_const_p:#FIXME:条件見直し
                    for j in range(i-2, -1, -1):#FIXME:なんかおかしい？
                        cost += self.move_w[j]*2
                return cost
        return 0

    # 修正版
    # p1 と p2 のパス相違度
    def __move_cost_fixed(self, p1, p2):
        p1_list = p1.split("/")
        p2_list = p2.split("/")
        cost = 0
        for i in range(0, max(len(p1_list), len(p2_list))):
            # 片方だけパスがあるなら1*wコスト加算確定
            if(i < min(len(p1_list), len(p2_list))):
                # 共通フォルダならコストを加算しない
                if(p1_list[i] == p2_list[i]): continue
            # 重みの決定
            if((i-2) > (len(self.move_w) -1)):
                weight = 1
            else:
                weight = self.move_w[i-2]
            # コストの加算
            if(i <= min(len(p1_list), len(p2_list))):
                cost += 2 * weight
            else:
                cost += 1 * weight
        return cost
                
    # 更新時刻の交錯でログを分割
    def __split_with_cross_mtime(self, left, right):
        result = [left]
        cp = left
        sp = self.__search_right(cp, right)
        checked = [self.log[cp].file_path]
        while cp < right:
            cp+=1
            if not self.log[cp].file_path in checked:
                sp = max(sp, self.__search_right(cp, right))
            if cp == sp:
                result.append(sp)
                checked = []
        result.append(right)
        return result

    # 更新時刻の交錯でログを分割
    def __split_with_cross_mtime2(self, left, right):
        result = [left]
        cp = left
        sp = self.__search_right(cp, right)
        fflag = 1
        checked = [self.log[cp].file_path]
        while cp < right:
            cp+=1
            if fflag == 0:
                sp = max(sp, self.__search_right(cp, right))
                fflag = 1
            else:
                if not self.log[cp].file_path in checked:
                    sp = max(sp, self.__search_right_onlyfile(cp, right))
            if cp == sp:
                result.append(sp)
                fflag = 0
                checked = []
        result.append(right)
        return result    

    def __search_right(self, left, right):
        for i in range(right, left, -1):
            if (self.log[i].file_path == self.log[left].file_path) or (self.log[i].timestamp - self.log[left].timestamp <= datetime.timedelta(seconds=10)):
            #if (self.log[i].file_path == self.log[left].file_path):
                return i
        return left

    def __search_right_onlyfile(self, left, right):
        for i in range(right, left, -1):
            #if (self.log[i].file_path == self.log[left].file_path) or (self.log[i].timestamp - self.log[left].timestamp <= datetime.timedelta(seconds=10)):
            if (self.log[i].file_path == self.log[left].file_path):
                return i
        return left

    # タイムラインのすべての隣接する更新時刻が1秒以下なら Unmanaged == True
    def __is_unmanaged(self, left, right):
        return set([(self.log[i+1].timestamp-self.log[i].timestamp)<=datetime.timedelta(seconds=1) for i in range(left,right+1,1) if i<right-1])=={True}
