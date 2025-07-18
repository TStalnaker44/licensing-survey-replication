
import csv, copy, os, shutil
from .utils import getQuestions, getPidFilter
from .resp_config import REC_CONFIG

base_name = "coder_1.csv"
fixed_name = "reconciliation.csv"
output_name = "final_coding.csv"

def main():

    questions = getQuestions()
    
    path = os.path.join(REC_CONFIG.PATH, "response_coding", "code_files", base_name)
    base = readCSVFile(path, questions)

    path = os.path.join(REC_CONFIG.PATH, "response_coding", "code_files", fixed_name)
    fixed = readCSVFile(path, questions)

    combined = combine(base, fixed, questions)
    path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", output_name)
    writeToFile(combined, path, questions)
    copyToDataDirectory(path)

def readCSVFile(path, questions):
    d = {}
    pid_filter = getPidFilter()
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i > 0:
                pid = row[0]
                if pid.strip() != "" and not int(pid) in pid_filter:
                    d[pid] = {}
                    for j, column in enumerate(questions):
                        codes = row[j+2].strip() # Maybe consider checking if only first column should be skipped
                        if codes != "":
                            if codes.startswith("[") and codes.endswith("]"):
                                d[pid][column] = eval(codes)
                            else:
                                d[pid][column] = codes.split(", ")
    return d

def combine(d1, d2, questions):
    d3 = copy.deepcopy(d1)
    for pid in d1.keys():
        for question in questions:
            if d2[pid].get(question, False):
                d3[pid][question] = d2[pid][question]
            elif d1[pid].get(question, False):
                d3[pid][question] = d1[pid][question]
    return d3

def writeToFile(d, fileName, questions):
    with open(fileName, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([""] + questions)
        for pid in d.keys():
            row = [pid]
            for i, q in enumerate(questions):
                if d[pid].get(q):
                    resp = d[pid][q]
                    row.append(str(resp))
                else:
                    row.append("")
            writer.writerow(row)
                    
def copyToDataDirectory(file):
    target = os.path.join(REC_CONFIG.PATH, "data", "response_coding.csv")
    shutil.copy(file, target)

if __name__ == "__main__":
    main()
