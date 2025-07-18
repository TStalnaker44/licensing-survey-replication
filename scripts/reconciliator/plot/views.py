from django.shortcuts import render
from .scripts.plotter import Plotter
from .scripts.generateReport import ReportGenerator
from global_vals import get_survey_internal
import json

def showPlot(request):

    p = Plotter()

    qid = request.GET.get("qid", p.getQuestionIDs()[0])
    qpart = request.GET.get("qpart")
    apart = request.GET.get("apart")
    if apart == "SHOW ALL": apart = None
    part = True if request.GET.get("part", "false") == "true" else False
    stack = True if request.GET.get("stack", "false") == "true" else False
    qtype = p.qtypes[qid]
    
    categories = []
    if qtype == "matrix":
        for qids in p.questions.values():
            if qid in qids:
                categories = qids.get(qid).get('options')
                break
    if categories:
        category = request.GET.get("cat", categories[0])
    else:
        category = None

    questions = p.getQuestionIDs()
    if qid not in questions:
        qid = questions[0]
        
    question_labels = [f"{p.getQuestionNameFromID(q)}: {p.getQuestionText(q)}" for q in questions]

    questions = list(zip(questions, question_labels))

    answers = [] if not qpart else p.getPossibleAnswers(qpart) + ["SHOW ALL"]
    qtext = p.getQuestionText(qid)
    qtype = p.getQuestionType(qid)

    data = {}
    if qtype == "ranked":
        with open(f"surveys/{get_survey_internal()}/questions.json", 'r') as file:
            for item in list(json.load(file).values()):
                if item.get(qid, {}) != {}:
                    labels = item.get(qid).get('options')
                    break
    elif qtype == "matrix":
        labels = [label.replace("'", "`") for label in getMatrixLabels(p, qid)]
        labels.append("Total Population")
    else:
        labels = [label.replace("'", "`") for label in p.getResults(qid)]


    if (part and qpart) and not apart:
        datasets = []
        for answer in answers[:-1]:
            temp = {}
            temp["label"] = answer.replace("'", "`")
            conditions = [{"question":qpart, "answers":[answer]}]
            valid = p.getFilteredResponses(conditions)
            hits = p.getResults(qid, valid)
            temp["data"] = [hits.get(label.replace("`", "'"), 0) for label in labels]
            datasets.append(temp)
        data = {"labels":labels, "datasets":datasets}
    elif part and qpart and apart:
        conditions = [{"question":qpart, "answers":[apart]}]
        valid = p.getFilteredResponses(conditions)
        codes = p.getResults(qid, valid)
        labels = [label.replace("'", "`") for label in codes]
        values = list(codes.values())
        data = {"labels":labels, "datasets":[{"label":apart, "data":values}]}
    else:
        if qtype == "matrix":
            counts = p.getResults(qid)[category]
            values = [ counts.get(label.replace("`", "'"), 0) for label in labels ]
        else:
            values = list(p.getResults(qid).values())
        if qtype == "ranked":
            color_ordered_data = list(zip(*values))
            num_colors = 0
            bar_color_codes = ["rgba(16, 85, 64, .85)", # W&M Green
                               "rgba(245, 179, 20, .85)", # W&M Yellow
                               "rgba(0, 0, 139, .85)", # Dark Blue
                               "rgba(176, 48, 96, .85)", # Maroon
                               "rgba(255, 0, 0, .85)", # Red
                               "rgba(0, 255, 0, .85)", # Lime Green
                               "rgba(0, 255, 255, .85)", # Aqua
                               "rgba(255, 0, 255, .85)", # Fuchsia
                               "rgba(100, 149, 237, .85)", # Cornflower
                               "rgba(255, 218, 185, .85)" # Peach
                            ]
            datasets = []
            for bar in color_ordered_data:
                bar_dict = {"label":ordinal(num_colors), 
                            "data":list(bar), 
                            "backgroundColor":bar_color_codes[num_colors%(len(bar_color_codes))]}
                if not stack:
                        bar_dict["stack"] = f"Stack{num_colors}"
                datasets.append(bar_dict)
                num_colors += 1
            data = {"labels":labels, "datasets":datasets} 
        else:
            data = {"labels":labels, "datasets":[{"data":values}]} 

    height = max(len(labels) * len(data["datasets"]) * 5, 150)

    totals = []
    for value in data["datasets"]:
        totals.append(value["data"][-1])
    totals = str(totals)

    data = str(data)
    
    return render(request, 'plot.html', {"data":data, "questions":questions,
                                         "qid":qid, "qtext":qtext , "qpart":qpart, "qtype": qtype,
                                         "answers":answers, "apart":apart, "part":part,
                                         "stack":stack, "height":height, "totals":totals,
                                         "categories":categories, "category":category})

def showReport(request):
    formats = ["table", "list"]
    report_format = request.GET.get("format", "table")
    percents = True if request.GET.get("percents", "false") == "true" else False

    # conditions = [{"question":"C3_tools", "answers":["codellama"]},
    #             {"question":"C3_tools", "answers":["phind"]}]
    conditions = []
    rg = ReportGenerator()
    qids = rg.getQuestionIDs()
    report = {}
    contains_rank = False
    for qid in qids:
        qtext = rg.getQuestionText(qid)
        qtype = rg.qtypes[qid]
        if conditions:
            hits = rg.getFilteredResponses(conditions)
            results = rg.getResults(qid, hits)
        else: 
            if qtype == "ranked": 
                if not contains_rank: contains_rank = True
                if percents:
                    results = rg.getResults(qid)
                    for key, value in results.items():
                        if key != "Total Population":
                            results[key] = [value[0]] + [round(count * 100/30, 2) for count in value[1:]]
                else: 
                    results = rg.getResults(qid)
            else:
                results = rg.getResults(qid)


        report[qid] = {"results":results, "qname": rg.getQuestionNameFromID(qid), "qtext":qtext, "qtype":qtype}

        
    return render(request, "report.html", {"report":report,
                                           "report_format":report_format,
                                           "contains_rank":contains_rank,
                                           "percents":percents})

def showComparisonTable(request):

    qid = request.GET.get("qid", ReportGenerator().getQuestionIDs()[0])
    # GET is a QueryDict
    qpart = request.GET.get("qpart", qid) # TODO: Replace D5 with the first question for the current survey

    rg = ReportGenerator()
     
    report = {"question":{
                "qid":qid,
                "qtext":rg.getQuestionText(qid),
                "answers":[]},
              "partition":{
                "question":{
                    "qid":qpart, 
                    "qtext":rg.getQuestionText(qpart)},
                "results":{}
                }
            }
    
    questions = rg.getQuestionIDs()
    qtypes = rg.getQuestionTypes(questions)
    for index in range(len(qtypes)-1,-1,-1):
        if qtypes[index] == "ranked": del questions[index]
    question_labels = [f"{rg.getQuestionNameFromID(q)}: {rg.getQuestionText(q)}" for q in questions]
    questions = list(zip(questions, question_labels))
    
    results = {}
    if rg.qtypes[qpart] != "ranked":
        answers = rg.getPossibleAnswers(qpart) 
        for answer in answers:
            conditions = [{"question":qpart, "answers":[answer]}]
            hits = rg.getFilteredResponses(conditions)
            results[answer] = rg.getResults(qid, hits)
        report["partition"]["results"] = results

        report["question"]["answers"] = results[list(results.keys())[0]].keys()

    return render(request, 'comparison.html', {"report":report, "questions":questions})

def ordinal(number):
    last_digit = str(number+1)[-1]
    if last_digit == '1': return "1st"
    if last_digit == '2': return "2nd"
    if last_digit == '3': return "3rd"
    return f"{last_digit}th"

def getMatrixLabels(p, qid):
    for gname, gdata in p.questions.items():
        for qname, qdata in gdata.items():
            if qname == qid:
                return qdata.get("answers")