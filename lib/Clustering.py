import numpy as np
import scipy
import re
import scipy.spatial.distance as distance
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
            
class ClusterHierarchy:
    def __init__(self, label, data, ans_label):
        self.label = label[:]
        self.data = data
        if ans_label==None:
            self.ans_label = ans_label
        else:
            self.ans_label = ans_label[:]
        self.answer_set = []
        self.cluster = None
        self.linked = None
        self.threshold = None
        self.threshold_prop = None
        self.purity = None
        self.ipurity = None
        self.fmeasure = None
        if self.ans_label != None:
            anss = list(set(self.ans_label))
            label_tmp = self.label[:]
            anslabel_tmp = self.ans_label[:]
            for ans in anss:
                if ans=="None": continue
                answer = []
                for i in range(anslabel_tmp.count(ans)):
                    idx = anslabel_tmp.index(ans)
                    anslabel_tmp.pop(idx)
                    answer.append(label_tmp.pop(idx))
                self.answer_set.append(answer)

    def linkage(self, method="average", metric="euclidean"):
        self.linked = linkage(self.data, method=method, metric=metric)

    def div(self, threshold):
        self.threshold = threshold
        self.cluster = fcluster(self.linked, self.threshold, criterion='distance')

    def fmax_div(self):
        fmax = 0
        for rate in range(1000):
            cluster_set = []
            threshold_tmp = rate/1000 * np.max(self.linked[:, 2])
            cluster_label = fcluster(self.linked, threshold_tmp, criterion='distance')
            for ci in range(max(cluster_label)):
                indexes = [i for i, x in enumerate(cluster_label) if x == (ci+1)]
                cluster = []
                for idx in indexes:
                    cluster.append(self.label[idx])
                cluster_set.append(cluster)
            ct = self.__cross_table(cluster_set,self.answer_set)
            p_tmp =self. __purity(ct)
            ip_tmp = self.__ipurity(ct)
            f = self.__fmeasure(p_tmp,ip_tmp)
            if(fmax < f):
                p = p_tmp
                ip = ip_tmp
                fmax = f
                threshold = threshold_tmp
                pth = rate/1000
        self.purity = p
        self.ipurity = ip
        self.fmeasure = fmax
        self.threshold = threshold
        self.threshold_prop = pth
        self.cluster = fcluster(self.linked, self.threshold, criterion='distance')

    def print_result(self):
        print(self.cluster)
        for ci in range(max(self.cluster)):
            indexes = [i for i, x in enumerate(self.cluster) if x == (ci+1)]
            print("\n--------------------Cluster", ci+1,"--------------------")
            for idx in indexes:
                print(self.label[idx],self.ans_label[idx])
        print("\nThreshold:",self.threshold_prop)
        print("Purity =", self.purity)
        print("I-Purity =", self.ipurity)
        print("F =", self.fmeasure)

        
    def print_result_fortex(self):
        num = 1
        for ci in range(max(self.cluster)):
            indexes = [i for i, x in enumerate(self.cluster) if x == (ci+1)]
            print("\hadashline")
            for idx in indexes:
                if self.ans_label[idx]!="None":
                    iswd = "○"
                else:
                    iswd = ""
                print(num,"&",self.label[idx],"&",self.ans_label[idx],"&","\\")
                num+=1
        print("\nThreshold:",self.threshold_prop)
        print("Purity =", self.purity)
        print("I-Purity =", self.ipurity)
        print("F =", self.fmeasure)

    def print_cluster(self):
        print(self.cluster)
        for ci in range(max(self.cluster)):
            indexes = [i for i, x in enumerate(self.cluster) if x == (ci+1)]
            print("\n--------------------Cluster", ci+1,"--------------------")
            for idx in indexes:
                print(self.label[idx])

    def get_cluster(self):
        cluster = []
        for ci in range(max(self.cluster)):
            elements = []
            indexes = [i for i, x in enumerate(self.cluster) if x == (ci+1)]
            for idx in indexes:
                elements.append(self.label[idx])
            cluster.append(elements)
        return cluster
        
    def __cross_table(self, cluster, answer, ignore="None"):
        table = []
        for c in cluster:
            row = []
            ignored_c = list(np.delete(np.array(c), [i for i, x in enumerate(c) if self.ans_label[self.label.index(x)] == ignore]))
            for a in answer:
                row.append(len(set(ignored_c)&set(a)))
            table.append(row)
        return table
        
    def __purity(self, ctable):
        s = 0
        n = 0
        for row in ctable:
            s+=max(row)
            n+=sum(row)
        return s/n

    def __ipurity(self, ctable):
        s = 0
        n = 0
        tctable = list(map(list,zip(*ctable)))
        for row in tctable:
            s+=max(row)
            n+=sum(row)
        return s/n
            
    def __fmeasure(self, p,ip):
        return 2/(1/p+1/ip)

    # Only use myself
    def save_dendrogram(self):
        label_s = []
        for path in self.label:
            label_s.append(re.sub(r'/home/ryota/.*/','',path)) # Please change to replace your home dir
        plt.figure(num=None, figsize=(16, 9), dpi=150, facecolor='w', edgecolor='k')
        dendrogram(self.linked, orientation='left', labels=label_s, leaf_font_size=8, color_threshold=self.threshold)
        plt.savefig("dendrogram.png")
