
import csv, os, json, shutil, glob
from .config import Config
from .manage_invalid import readInvalid

def partition(survey):
    Partition(survey).run()
    
class Partition():

    def __init__(self, survey):
        self._survey = survey
        self._config = Config(survey)
        self._partitions = self._config.partitions

    def run(self):
        codes = self.getCodingData()
        data = self.getJsonData()
        self.saveAll()
        for pname, pdata in self._partitions.items():
            self.saveLoose(codes, data, pname, pdata)
            self.saveStrict(codes, data, pname, pdata)

    def getDataPath(self):
        return os.path.join(self._survey, "data")

    def getFilePath(self):
        return os.path.join(self._survey, "files")

    def getMostRecent(self):
        path = os.path.join(self.getFilePath(), "*sanitized_*.json")
        return glob.glob(path)[-1]

    def getCodingData(self):
        path = os.path.join(self.getDataPath(), "response_coding.csv")
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            return [row for row in reader]
        
    def getJsonData(self):
        path = self.getMostRecent()
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
        
    def saveAll(self):
        shutil.copy(os.path.join(self.getDataPath(), "response_coding.csv"),
                    os.path.join(self.getDataPath(), "all", "response_coding.csv"))
        
    def getRole(self, data, pid, pdata):
        if pid not in readInvalid():
            group, question = pdata["path"]
            answer = data[pid][group][question]
            if isinstance(answer, str):
                return [answer]
            else:
                return answer["answers"]
        else:
            return None

    def saveLoose(self, codes, data, pname, pdata):
        partitions = pdata["partitions"]
        if self.checkParitionExists(pname, "loose"):
            for r in partitions.keys():
                path = os.path.join(self.getDataPath(), "partitions", pname, "loose", r)
                if os.path.exists(path):
                    fname = os.path.join(path, "response_coding.csv")
                    with open(fname, "w", encoding="utf-8") as file:
                        writer = csv.writer(file, lineterminator='\n')
                        for i, row in enumerate(codes):
                            if i == 0:
                                writer.writerow(row)
                            else:
                                pid = row[0]
                                role = self.getRole(data, pid, pdata)
                                if role != None and partitions[r] in role:
                                    writer.writerow(row)

    def saveStrict(self, codes, data, pname, pdata):
        partitions = pdata["partitions"]
        if self.checkParitionExists(pname, "strict"):
            for r in partitions:
                path = os.path.join(self.getDataPath(), "partitions", pname, "strict", r)
                if os.path.exists(path):
                    fname = os.path.join(path, "response_coding.csv")
                    with open(fname, "w", encoding="utf-8") as file:
                        writer = csv.writer(file, lineterminator='\n')
                        for i, row in enumerate(codes):
                            if i == 0:
                                writer.writerow(row)
                            else:
                                pid = row[0]
                                target = set([partitions[role] for role in r.split("-")])
                                role = self.getRole(data, pid, pdata)
                                if role != None and target == role:
                                    writer.writerow(row)

    def checkParitionExists(self, pname, level):
        path = os.path.join(self.getDataPath(), "partitions", pname, level)
        return os.path.isdir(path)

    
