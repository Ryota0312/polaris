import csv
import re
from pathlib import Path

class Database:
    def __init__(self, filename):
        self.filename = filename
        Path(self.filename).touch()
        self.data = self.__read()
        # TODO: hash（1列目キー，2,3列目バリュー）として保持する方が効率良い

    def __read(self):
        ret = []
        with open(self.filename, "r") as f:
            #return [line.replace("\n", "").split(",", 1) for line in f]
            #for line in f:
            #    l = line.replace("\n", "").split(",", 1)
            #    l2 = l[1].rsplit(",", 1)
            #    ret.append([l[0], l2[0], l2[1]])
            #return ret
            for i, line in enumerate(f):
                #if i==0: continue
                m = re.match("(.*),(\[.*\]),(\[.*\])", line)
                ret.append([m.group(1), m.group(2), m.group(3)])
            return ret
                
    def __write_csv(self): 
        with open(self.filename, 'w', newline='') as f:
            for l in self.data: f.write(l[0] + "," + l[1] + "," + l[2] + "\n")
            
    def update(self, label, new_data1, new_data2):
        update_flag = 0
        for d in self.data:
            if d[0]==label:
                d[1] = new_data1
                d[2] = new_data2
                update_flag = 1
        if update_flag == 0:
            self.data.append([label, new_data1, new_data2])
        self.__write_csv()

    def get(self, label):
        for d in self.data:
            if d[0] == label:
                try:
                    return eval(d) #evalするかどうかは使い手が決めるべきかも
                except:
                    return []
        return [] # None を返して処理は他に任せたほうが良い
