from global_vals import get_survey_internal
import json, os, glob

def readJSON(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
def getMostRecent(survey):
    path = os.path.join(survey, "files", "*sanitized_*.json")
    return glob.glob(path)[-1]

class Browser():

    def __init__(self):
        survey_path = os.path.join("surveys", get_survey_internal()) 
        self.qdata = readJSON(os.path.join(survey_path, "questions.json"))
        self.rdata = readJSON(os.path.join(survey_path, "files", "results.json"))
        self.question_mapping = self.getQuestionMapping()
        most_recent = getMostRecent(survey_path)
        self.responses = readJSON(most_recent)

    def getQuestionMapping(self):
        mapping = {}
        for gname, gdata in self.qdata.items():
            for qname, qdata in gdata.items():
                mapping[qname] = gname
        return mapping
    
    def getQIDs(self):
        qids = {}
        for gname, gdata in self.qdata.items():
            for qname, qdata in gdata.items():
                if qdata.get("coded"):
                    qids[qname] = qdata["question"]
        return qids
    
    def getCodes(self, question):
        codes = {}
        for value in self.rdata[question].values():
            for code in value:
                if code not in codes:
                    codes[code] = 1
                else:
                    codes[code] += 1
        codes = [(code.replace("'", ""), code.replace("_", " "), count) for code, count in codes.items()]
        codes = sorted(codes, key=lambda x: x[2], reverse=True)
        return codes
    
    def validPids(self, question, code):
        pids = []
        for pid, response in self.rdata[question].items():
            if any(code == r.replace("'", "") for r in response):
                pids.append(pid)
        return pids
    
    def getResponses(self, question, code):
        pids = self.validPids(question, code)
        gname = self.question_mapping[question]
        responses = {}
        for pid, resp_data in self.responses.items():
            if pid in pids:
                response = resp_data[gname][question]
                responses[pid] = response
        return responses
