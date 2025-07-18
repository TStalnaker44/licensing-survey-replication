
import json, os
from .utils import getQuestions, readCodeFiles, all_combinations
from .resp_config import REC_CONFIG

input_file_template = "coder_%d.csv" # Format of the coded file names
output_file = "response_codes.json"         # Name of the output file

def createFormattedJSON(coders, questions):
    d = {}
    for q in questions:
        d[q] = {}
        for pid in coders[0].keys():
            d[q][pid] = {}
            for i, coder in enumerate(coders):
                d[q][pid][f"R{i}"] = list(coder[pid][q])
    return d

def addCodeToLabel(d, code, label):
    if label in d:
        d[label].append(code)
    else:
        d[label] = [code]

def getAllCodes(coders):
    all_codes = []
    for coder in coders:
        all_codes.extend(coder)
    return set(all_codes)

def addLabels(d, coders):
    labels = all_combinations([f"R{i}" for i in range(len(coders))])
    for label in labels:
        d[label] = []

def main():
    questions = getQuestions()
    coders = readCodeFiles(questions)
    d = createFormattedJSON(coders, questions)

    # Create unique JSON (conveys more information)
    uniques = {}
    ids = coders[0].keys()

    for q in questions:
        uniques[q] = {}

        for pid in ids:

            responses = {}

            # Get all codes for the question
            coders = d[q][pid].values()
            addLabels(responses, coders)
            all_codes = getAllCodes(coders)

            # Determine who used each code (the label)
            for code in all_codes:
                label = ""
                for i, coder in enumerate(coders):
                    if code in coder:
                        label += f"R{i}"
                addCodeToLabel(responses, code, label)

            uniques[q][pid] = responses

    path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", output_file)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(uniques, file)

if __name__ == "__main__":
    main()