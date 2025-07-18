
import json, os
from collections import Counter
from global_vals import get_survey_internal
# from scripts.reconciliator.data_analysis.scripts.results_json import getQIDMapping
from data_analysis.scripts.results_json import getQIDMapping

SINGLE_ANSWER = ("single-select", "single-select-with-other", "likert", "single-text")
LIST_ANSWER   = ("multi-select", "multi-select-with-other", "short-answer", "cleaned", "ranked", "matrix")

# SURVEY = "quantum" # Add input to make this more generalizable
# SURVEY = "math"

def readJson(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

class ReportGenerator():

    def __init__(self):
        self.questions = self.getQuestions()
        self.qname_to_qid_mapping = getQIDMapping(self.questions)
        self.data = self.getData()
        self.qids = self.getQuestionIDs()
        self.getQuestionInfo()
        self.results = {qid:{} for qid in self.qids}
        
        # Map question ids to names (basically a reverse of the main mapping)
        self.qid_to_qname_mapping = {v: k for k, v in self.qname_to_qid_mapping.items()}

    def getQuestions(self):
        return readJson(os.path.join("surveys", get_survey_internal(), "questions.json"))
    
    def getData(self):
        return readJson(os.path.join("surveys", get_survey_internal(), "files", "results.json"))
    
    def getQuestionIDs(self):
        return list(self.data.keys())
    
    def getQuestionNameFromID(self, qid):
        return self.qid_to_qname_mapping[qid]
    
    def getQuestionText(self, qid):
        return self.qtexts[qid]
    
    def getQuestionTypes(self, qids):
        return [self.qtypes[qid] for qid in qids]
    
    def getQuestionType(self, qid):
        return self.qtypes[qid]
        
    def getQuestionInfo(self):
        self.qtypes = {}
        self.qtexts = {}
        
        for gname, gdata in self.questions.items():
            for qname, qdata in gdata.items():
                qid = self.qname_to_qid_mapping[qname]
                
                self.qtypes[qid] = qdata.get("type")
                self.qtexts[qid] = qdata["question"]
                
        for qid in self.qids:
            if qid not in self.qtypes:
                self.qtypes[qid] = "cleaned"
                self.qtexts[qid] = self.qtexts[qid.split("_")[0]]
    
    """
    conditions = [{'question':"<question id>",
                   'answers':['a1',a2,a3]}] # This is an OR relationship

    conditions = [{"question":"C3_tools", "answers":["codellama"]},
                  {"question":"C3_tools", "answers":["phind"]}] # This is an AND
    """

    def answerMatch(self, qid, answer, response):
        qtype = self.qtypes[qid]
        if qtype in SINGLE_ANSWER:
            return response.lower() == answer.lower()
        if qtype in LIST_ANSWER:
            return answer.lower() in map(lambda x: x.lower(), response)
        return False

    def getFilteredResponses(self, conditions):
        hits = []
        for condition in conditions:
            # qid here *probably* refers to a name, but I'll use .get just in case
            qname = condition["question"]
            qid = self.qname_to_qid_mapping.get(qname, qname)
            
            answers = condition["answers"]
            valid = set()
            for pid, response in self.data[qid].items():
                for a in answers:
                    if self.answerMatch(qid, a, response):
                        valid.add(pid)
            hits.append(valid)
        return set.intersection(*hits)
    
    def getResults(self, qid, valid=None):
        data = self.data[qid]
        if valid == None: valid = list(data.keys())
        results = []
        resp_count = 0
        for pid, response in data.items():
            if pid in valid:
                qtype = self.qtypes[qid]
                if qtype in SINGLE_ANSWER and response != "":   
                    results.append(response)
                    resp_count += 1
                elif qtype in LIST_ANSWER and not response in ([], [""]):
                    if qtype in  ("ranked", "matrix"):
                        results.append(list(response.values()))
                    else:
                        results.extend(response)
                    resp_count += 1
        return self.processResults(results, resp_count, qid)
    
    def formatReturn(self, count, total):
        if total:
            percent = round((count/total)*100, 2)
            if percent.is_integer(): percent = int(percent)
        else: percent = 0
        return {"count":count, 
                "percent":percent}
    
    def sortResults(self, result, qid):
        response = result[0]
        count = result[1]

        if self.qtypes[qid] == "likert":
            for gname, gdata in self.questions.items():
                for qname, qdata in gdata.items():
                    qid2 = self.qname_to_qid_mapping[qname]
                    
                    if qid == qid2:
                        answers = list(qdata["options"]) # This is where the error is
                        # answers.reverse()
                        return answers.index(response)
        else:
            return count
            
    def processResults(self, results, total, qid):
        qtype = self.qtypes[qid]
        if qtype == "ranked":
            with open(f"surveys/{get_survey_internal()}/questions.json", 'r') as file:
                for item in list(json.load(file).values()):
                    if item.get(qid, {}) != {}:
                        labels = item.get(qid).get('options')
                        break
            total_choices = len(results[0])
            results_temp = {}
            for ans in range(1, total_choices+1):
                num_responses = 0
                cur_results = [0] #Index 0 holds the average rank for the given answer
                for i in range(total_choices):
                    counter = 0
                    for response in results:
                        if response[i] == str(ans): counter += 1
                    num_responses += counter
                    cur_results[0] += counter * (i+1)
                    cur_results.append(counter)
                cur_results[0] /= num_responses
                cur_results[0] = round(cur_results[0], 2)
                results_temp[labels[ans-1]] = cur_results
            results = results_temp
        elif qtype == "matrix":
            for qids in self.questions.values():
                if qid in qids:
                    subquestions = qids.get(qid).get('options')
                    break
            combined_results = {}
            for i, subquestion in enumerate(subquestions):
                subresults = [answer[i] for answer in results]
                subresults = self.formatResults(subresults, total, qid)
                combined_results[subquestion] = subresults
            results = combined_results
        else:
            results = self.formatResults(results, total, qid) 
        return results

    def formatResults(self, results, total, qid):
        results = [(result, count) for result, count in Counter(results).items()]
        answers = self.getPossibleAnswers(qid)
        for a in answers:
            if not any([a == r[0] for r in results]):
                results.append((a, 0)) 
        results = sorted(results, key=lambda x: self.sortResults(x, qid), reverse=True)
        results = {resp:self.formatReturn(count, total) for resp, count in results}
        results["Total Population"] = self.formatReturn(total, total)
        return results
    
    def getPossibleAnswers(self, qid):
        data = self.data[qid]
        responses = set()
        qtype = self.qtypes[qid]
        for response in data.values():
            if qtype in SINGLE_ANSWER and response != "":
                responses.add(response)
            elif qtype in LIST_ANSWER and not response in ([], [""]):
                if qtype == "matrix":
                    for resp in response.values():
                        responses.add(resp)
                else:
                    responses.update(list(response))
        return sorted(list(responses))