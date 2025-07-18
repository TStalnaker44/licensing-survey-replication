
import os

class PathManager():

    def __init__(self, directory):
        self.dir = directory
        self.role = ""
        self.part = ""
        self.strict = False

    def getDataPath(self):
        if self.role == "":
            return os.path.join(self.dir, "data", "all")
        else:
            if self.strict:
                return os.path.join(self.dir, "data", "partitions", self.part, "strict", self.role)
            else:
                return os.path.join(self.dir, "data", "partitions", self.part, "loose", self.role)
                
    def getFigPath(self):
        if self.role == "":
            self.mkdir("all")
            return os.path.join(self.dir, "figs", "all")
        else:
            if self.strict:
                self.mkdir("partitions", self.part, "strict", self.role)
                return os.path.join(self.dir, "figs", "partitions", self.part, "strict", self.role)
            else:
                self.mkdir("partitions", self.part, "loose", self.role)
                return os.path.join(self.dir, "figs", "partitions", self.part, "loose", self.role)

        
    def mkdir(self, *path):
        folders = os.path.sep.join(path).split(os.path.sep) ## Path components may themselves be paths
        for i in range(1, len(folders)+1):
            temp = os.path.join(self.dir, "figs", os.path.join(*folders[:i]))
            if not os.path.isdir(temp):
                os.mkdir(temp)

    def setPartition(self, part):
        self.part = part
        self.makePartDirectory()

    def makePartDirectory(self):
        path = os.path.join(self.dir, "figs", "partitions", self.part)
        if not os.path.isdir(path):
            os.mkdir(path)

    def makeTopLevelPartDirectory(self):
        path = os.path.join(self.dir, "figs", "partitions")
        if not os.path.exists(path):
            os.mkdir(path)