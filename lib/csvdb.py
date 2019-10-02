import csv

class Database:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.__read()

    def __read(self):
        with open(self.filename, "r") as f:
            return [line.replace("\n", "").split(",", 1) for line in f]
                
    def __write_csv(self): 
        with open(self.filename, 'w', newline='') as f:
            for l in self.data: f.write(l[0] + "," + l[1] + "\n")
            
    def update(self, label, new_data):
        update_flag = 0
        for d in self.data:
            if d[0]==label:
                d[1] = new_data
                update_flag = 1
        if update_flag == 0:
            self.data.append([label, new_data])
        self.__write_csv()
