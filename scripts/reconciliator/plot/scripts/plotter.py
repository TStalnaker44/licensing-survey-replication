
import os, json
from collections import Counter
from .generateReport import ReportGenerator
    
class Plotter(ReportGenerator):
    
    def __init__(self):
        ReportGenerator.__init__(self)
    
    # Plotter isn't currently able to support the added percentages from the ReportGenerator
    def processResults(self, results, count, qid):
        qtype = self.qtypes[qid]
        if qtype == "ranked":
            total_answers = len(results[0])
            results_temp = {}
            for ans in range(1, total_answers+1):
                cur_results = []
                for i in range(total_answers):
                    counter = 0
                    for response in results:
                        if response[i] == str(ans): counter += 1
                    cur_results.append(counter)
                results_temp[str(ans)] = cur_results
            results = results_temp
        elif qtype == "matrix":
            for qids in self.questions.values():
                if qid in qids:
                    subquestions = qids.get(qid).get('options')
                    break
            combined_results = {}
            for i, subquestion in enumerate(subquestions):
                subresults = [answer[i] for answer in results]
                subresults = [(result, count) for result, count in Counter(subresults).items()]
                subresults = sorted(subresults, key=lambda x: x[1], reverse=True)
                subresults = {resp:count for resp, count in subresults}
                subresults["Total Population"] = count
                combined_results[subquestion] = subresults
            results = combined_results
        else:
            results = [(result, count) for result, count in Counter(results).items()]
            results = sorted(results, key=lambda x: x[1], reverse=True)
            results = {resp:count for resp, count in results}
            results["Total Population"] = count
        return results
