import re
import datetime
import time
import numpy as np
import pickle

reg = r"(.*)(?:\.([^.]+$))"

# record style: "TIMESTAMP FILE_PATH OPERATION"" 
class AccessLog:
    def __init__(self, record, sep):
        sep1 = record.split(sep,1)
        sep2 = sep1[1].rsplit(sep,1)
        column = [sep1[0],sep2[0],sep2[1]]
        self.timestamp = datetime.datetime.strptime(column[0], '%Y-%m-%dT%H:%M:%S')
        self.file_path = column[1]
        self.operation = column[2]
        m = re.match(reg, self.file_path)
        if m:
            self.ext = m.group(2)
        else:
            self.ext = "None"

    def __eq__(self, other):
        return ((self.timestamp == other.timestamp) and (self.file_path == other.file_path) and (self.operation == other.operation))

class AccessLogCollection:
    def __init__(self, records=[]):
        self.records = records

    # len() method return num of records
    def __len__(self):
        return len(self.records)
        
    # [] method return AccessLog
    def __getitem__(self, key):
        return self.records[key]

    # add record to collection
    # FIX ME: 挙動がおかしい
    def append(self, record):
        self.records.append(record)

    # extend record collection to collection        
    def extend(self, record):
        self.records.extend(record.records)

    # Get file extension in AccessLogCollection
    def get_exts(self):
        exts = []
        reg = r"(.*)(?:\.([^.]+$))"
        for record in self.records:
            m = re.match(reg, record.file_path)
            if m:
                exts.append(m.group(2))
            else:
                exts.append(None)
        return list(set(exts))
        
    # Filter and return AccessLogCollection
    # return records that the timestamp in range from start to end 
    def time_filter(self, start, end):
        filtered = []
        for record in self.records:
            if start <= record.timestamp <= end:
                filtered.append(record)
        return AccessLogCollection(filtered)
    
    # file_path="regex"
    def path_filter(self, path):
        filtered = []
        for record in self.records:
            if re.match(path, record.file_path):
                filtered.append(record)
        return AccessLogCollection(filtered)
    
    # operation=string
    def op_filter(self, operation):
        filtered = []
        for record in self.records:
            if re.match(operation, record.operation):
                filtered.append(record)
        return AccessLogCollection(filtered)

    def ext_filter(self, ext):
        reg = r"(.*)(?:\.([^.]+$))"
        filtered = []
        for record in self.records:
            m = re.match(reg, record.file_path)
            if m:
                e = m.group(2)
            else:
                e = None
            if e in ext: filtered.append(record)
        return AccessLogCollection(filtered)        

# Parse log file and return AccessLogCollection
# TODO: 名称変更されたファイル，フォルダを追跡する．追跡失敗した場合，手動で置き換えられるようにする．
class LogParser:
    def __init__(self, sep=" "):
        self.sepstr = sep
        self.log = None

    def parse(self, logfile_path):
        log = []
        access_log = open(logfile_path, "r")
        for line in access_log:
            log_t = AccessLog(line.replace("\n",""), self.sepstr)
            if len(log) > 0:
                if log_t == log[len(log)-1]: continue
            log.append(log_t)
        access_log.close()
        self.log = AccessLogCollection(log)
        return self.log

    def update(self, logfile_path):
        log = []
        access_log = open(logfile_path, "r")
        lines = access_log.readlines()
        for i in range(len(lines)-1,0,-1):
            log_t = AccessLog(lines[i].replace("\n",""), self.sepstr)
            if log_t == self.log[len(self.log)-1]: break
            if len(log) > 0:
                if log_t == log[len(log)-1]: continue
            log.insert(0,log_t)
        alc = AccessLogCollection(log)
        self.log.extend(alc)
        return self.log

    def dump(self):
        with open('log.pickle', mode='wb') as f:
            pickle.dump(self.log, f)

    def load(self):
        with open('log.pickle', mode='rb') as f:
            self.log = pickle.load(f)
        return self.log

class ConvolutionFilter:
    def __init__(self, size, stride):
        self.size = size
        self.stride = stride

    def convolution(self, ary):
        conv_ary = []
        for i in range(0,len(ary)-1,self.stride):
            conv_ary.append(sum(ary[i:i+self.size]))
        return conv_ary
