
import os
from .resp_config import REC_CONFIG
from .utils import getQuestions, readCodeFiles, getPidFilter

output_file = "diff_locations.csv"   # Name of the output file
diff_file = "diffs.csv"              # Name of the diffs file

class Comparer():

    def __init__(self):
        self.questions = getQuestions()
        self.codes = readCodeFiles(self.questions)

    def run(self):
        matches = self.makeComparison()
        self.saveToFile(matches)
        self.writeDiffs(matches)

    def makeComparison(self):
        lyst = []
        for pid in self.codes[0].keys():
            for question in self.questions:
                coder_1 = self.codes[0][pid].get(question, None)
                if all(coder_1 == coder[pid].get(question, None) for coder in self.codes):
                    if not int(pid) in getPidFilter():
                        lyst.append((pid, question))
        return lyst

    def getDiffs(self, pid, question):
        lists = [code[pid][question] for code in self.codes]

        all_elements = set(item for sublist in lists for item in sublist)
        elements_not_in_all = []

        for element in all_elements:
            count = sum(1 for sublist in lists if element in sublist)
            if count < len(lists):
                elements_not_in_all.append(element)

        return elements_not_in_all

    def writeDiffs(self, matches):
        path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", diff_file)
        with open(path, "w", encoding="utf-8") as file:
            file.write("," + ",".join(self.questions) + "\n")
            for pid in self.codes[0].keys():
                file.write(pid + ",")
                for q in self.questions:
                    if (pid, q) in matches:
                        file.write("[],")
                    else:
                        diffs = self.getDiffs(pid, q)
                        diffs = '"' + str(diffs) + '"'
                        file.write(diffs+",")
                file.write("\n")
            file.flush()

    def saveToFile(self, matches):
        path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", output_file)
        with open(path, "w", encoding="utf-8") as file:
            file.write("," + ",".join(self.questions) + "\n")
            for pid in self.codes[0].keys():
                file.write(pid + ",")
                for q in self.questions:
                    if (pid, q) in matches:
                        file.write(",")
                    else:
                        file.write("X,")
                file.write("\n")
            file.flush()

def main():
    c = Comparer()
    c.run()

if __name__ == "__main__":
    main()





