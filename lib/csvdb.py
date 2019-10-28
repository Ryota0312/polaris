import csv
import re
from pathlib import Path
import datetime
#TODO: 現状1列目がラベル，他2列がデータとなっているが汎用的にしたほうが良い
###### たとえば，ヘッダを作ってそれをキーとする辞書で保持する

class Database:
    def __init__(self, filename):
        self.filename = filename
        Path(self.filename).touch()
        self.data = self.__read()
        # TODO: hash（1列目キー，2,3列目バリュー）として保持する方が効率良い

    def __read(self):
        ret = []
        with open(self.filename, "r") as f:
            for i, line in enumerate(f):
                m = re.match("(.*),(\[.*\]),(\[.*\])", line)
                ret.append([m.group(1), m.group(2), m.group(3)])
            return ret
                
    def __write_csv(self): 
        with open(self.filename, 'w', newline='') as f:
            for l in self.data: f.write(l[0] + "," + l[1] + "," + l[2] + "\n")
            
    def update(self, label, new_data1, new_data2):
        update_flag = 0
        for i,d in enumerate(self.data):
            if d[0]==label:
                self.data[i][1] = new_data1
                self.data[i][2] = new_data2
                update_flag = 1
        if update_flag == 0:
            self.data.append([label, new_data1, new_data2])
        self.__write_csv()

    def get(self, label, row):
        for d in self.data:
            if d[0] == label:
                try:
                    return eval(d[row]) #evalするかどうかは使い手が決めるべきかも
                except:
                    return []
        return [] # None を返して処理は他に任せたほうが良い
