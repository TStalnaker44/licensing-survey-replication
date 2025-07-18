
import os, glob, json, csv
from .settings import CONFIG

def getMostRecent(survey):
    path = os.path.join(survey, "files", "*sanitized_*.json")
    return glob.glob(path)[-1].split(os.sep)[-1]

def readJson(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
    
def writeJson(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        
# Gets the question ID using the qname and qdata
def getQuestionID(qname, qdata):
    return qdata.get("qual_name", qname)
        
# Returns a mapping of question names to the actual question IDs
def getQIDMapping(questions):
    result = {}
        
    for group_data in questions.values():
        for qname, qdata in group_data.items():
            result[qname] = getQuestionID(qname, qdata)
            
    return result
    
class ResultsJson():

    def __init__(self):
        self.survey = os.path.join("surveys", CONFIG.SURVEY)
        self.questions = readJson(os.path.join(self.survey, "questions.json"))
        
        # Set the actual IDs to avoid needing to find them repeatedly later on
        self.qname_to_qid_mapping = getQIDMapping(self.questions)
        
        self.qids = self.getQuestionIDs()
        self.qtypes = self.getQuestionTypes()
        
        if CONFIG.RESPONSE_CODING_DONE:
            self.coded = self.getCodedQuestions()
            self.codes = self.getCodes()
        self.results = {qid:{} for qid in self.qids}

    def getQuestionIDs(self):
        ids = []
        for gdata in self.questions.values():
            for qname, qdata in gdata.items():
                if qdata.get("contains_pii"):
                    continue
                if qdata.get("coded") and not CONFIG.RESPONSE_CODING_DONE:
                    continue
                ids.append(self.qname_to_qid_mapping[qname])
        return ids
    
    def getQuestionTypes(self):
        types = {}
        for gdata in self.questions.values():
            for qname, qdata in gdata.items():
                types[self.qname_to_qid_mapping[qname]] = qdata["type"]
        return types
    
    def getCodedQuestions(self):
        coded = []
        for gdata in self.questions.values():
            for qname, qdata in gdata.items():
                if qdata.get("coded"):
                    # coded.append(qname)
                    # It is probably best to fix this potential bug in advance by having it use the actual Qualtrics ID
                    coded.append(self.qname_to_qid_mapping[qname])
        return coded
    
    def getCodes(self):
        path = os.path.join(self.survey, "response_coding", "generated_files", "final_coding.csv")
        with open(path, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            codes = {}
            for i, row in enumerate(reader):
                if i == 0:
                    for question in row[1:]:
                        codes[question] = {}
                        questions = row[1:]
                else:
                    pid = row[0]
                    for j, column in enumerate(row[1:]):
                        if column == "":
                            codes[questions[j]][pid] = []
                        else:
                            codes[questions[j]][pid] = eval(column)
            return codes
    
    def addData(self, qname, qdata, pid):
        qtype = self.qtypes[qname]
        if qtype in ("multi-select", "single-select", "single-text", "likert", "ranked", "matrix"):
            return qdata
        elif qtype in ("multi-select-with-other", "single-select-with-other"):
            return qdata["answers"]
        elif CONFIG.RESPONSE_CODING_DONE and (qname in self.coded):
            return self.codes[qname][pid]
        else:
            return []

    def makeResultsJson(self):
        most_recent = getMostRecent(self.survey)
        data = readJson(os.path.join(self.survey, "files", most_recent))
        for pid, responses in data.items():
            for gname, gdata in responses.items():
                for qname, qdata in gdata.items():
                    qid = self.qname_to_qid_mapping.get(qname, qname)
                    
                    if qid in self.results:
                        self.results[qid][pid] = self.addData(qid, qdata, pid)
        self.addCleanedData()
        writeJson(self.results, os.path.join(self.survey, "files", "results.json"))

    def addCleanedData(self):
        clean = self.getDataFromCleanup()
        for key, data in clean.items():
            base_question = key.split("_")[0]
            # if base_question in self.results:
            #     self.results.pop(base_question)
            self.results[key] = data

    def getDataFromCleanup(self):
        path = os.path.join(self.survey, "response_coding", "code_files", "response_clean_up.csv")
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:
                    data = {question:{} for question in row[2:]}
                    questions = row[2:]
                else:
                    pid = row[0]
                    for j, column in enumerate(row[2:]):
                        data[questions[j]][pid] = column.split(", ")
            return data