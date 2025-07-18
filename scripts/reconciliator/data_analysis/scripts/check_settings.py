
import os, json, glob
from .settings import CONFIG

def checkSettings():
    if not checkSurveys():
        return 0
    if not checkForSourceFiles():
        return 0
    if not checkPreprocess():
        return 0
    if not checkAbilityToPlot():
        return 0
    if not checkQuestionFiles():
        return 0
    if not checkMetaFiles():
        return 0
    if not checkSyntaxOfQuestionFiles():
        return 0
    if not checkResponseCoding():
        return 0
    return 1

def checkForSourceFiles():
    if CONFIG.FROM_SOURCE:
        path = os.path.join("surveys", CONFIG.SURVEY, "files", "data_*.csv")
        files = glob.glob(path)
        if len(files) == 0:
            print("FROM_SOURCE is set to True, but no files of type 'data_MM_DD_YY.csv' were found.")
            print(f"Please place your Qualtrics response export in the 'surveys/{CONFIG.SURVEY}/files' directory")
            print("Or set FROM_SOURCE to False, if you already have up-to-date sanitized JSON files.")
            return 0
    return 1

def checkPreprocess():
    if (not CONFIG.FROM_SOURCE) and CONFIG.PRE_PROCESS:
        survey = CONFIG.SURVEY
        path = os.path.join("surveys", survey, "files", "*_sanitized_*.json")
        files = glob.glob(path)
        if len(files) == 0:
            print(f"PRE_PROCESS is set to True, but no files of type '{survey}_sanitized_MM_DD_YY.json' were found.")
            print(f"Please create them by setting FROM_SOURCE to True and running this script again.")
            print(f"Or set PRE_PROCESS to False, if you already have up-to-date csv files in the '{survey}/data' directory.")
            return 0
    return 1

def checkAbilityToPlot():
    if (not CONFIG.PRE_PROCESS) and CONFIG.PLOT:
        survey = CONFIG.SURVEY
        path = os.path.join("surveys", survey, "data")
        if not os.path.exists(path):
            print(f"PLOT is set to True, but there is no data folder.")
            print(f"Please run this script with PRE_PROCESS set to True to create necessary files")
            return 0
    return 1

def checkResponseCoding():
    if CONFIG.RESPONSE_CODING_DONE:
        survey = CONFIG.SURVEY
        path = os.path.join("surveys", survey, "data", "response_coding.csv")
        if not os.path.exists(path):
            print(f"RESPONSE_CODING_DONE is set to True, but the 'response_coding.csv' file for '{survey}' could not be found.")
            print(f"Either set RESPONSE_CODING_DONE to False or place the appropriate file in the '{survey}/data' directory.")
            return 0
    return 1

def checkMetaFiles():
    missing = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "metafields.json")
    if not os.path.exists(path):
        missing.append(survey)
    if missing:
        print("The following surveys are missing metafields.json:", ", ".join(missing))
        for survey in missing:
            makeMetafields(survey)
        print("Added default metafield.json files to directories.")
        # print("For each survey, please:\n (1) Make sure that metafields.json is in the right location (the top-level of your survey directory)" +\
        #        "\n (2) Or make one by copying and editing the template provided in the documentation.")

    return 1

def checkQuestionFiles():
    missing = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "questions.json")
    if not os.path.exists(path):
        missing.append(survey)
    if missing:
        print("The following surveys are missing questions.json:", ", ".join(missing))
        print("For each survey, please:\n (1) Make sure that questions.json is in the right location (the top-level of your survey directory)" +\
               "\n (2) Or run createQuestionsJson.py to create one before continuing.")
        return 0
    return 1

def checkSyntaxOfQuestionFiles():
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "questions.json")
    with open(path, "r", encoding="utf-8") as file:
        d = json.load(file)
    questions = []
    for gname, gdata in d.items():
        for qname, qdata in gdata.items():
            if not qdata.get("question"):
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Missing 'question' tag on question {qname} in group '{gname}'")
                print("All questions must contain question text.")
                return 0
            if not qdata.get("type"):
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Missing 'type' tag on question {qname} in group '{gname}'")
                return 0
            if qdata.get("partition_on"):
                if not (qdata.get("partitions") and qdata.get("partition_name")):
                    print(f"Incorrect syntax in {survey}/questions.json")
                    print("When using the 'partition' tag you must also include 'partition_name' and 'partitions'")
                    print("See documentation for more details.")
                    return 0
            if qdata["type"] == "ranked" and (not qdata.get("options")):
                print(f"Incorrect syntax in {survey}/questions.json")
                print("Questions of type 'ranked' must include the 'options' tag")
                print("See documentation for more details.")
                return 0
            if qname in questions:
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Two questions with the name '{qname}'")
                print("All question names must be unique.")
                return 0
            questions.append(qname)

    return 1

def checkSurveys():
    if CONFIG.SURVEY in (None, ""):
        print("No surveys provided. Please provide at least one survey to begin.")
        return 0
    bad_surveys = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey)
    if not os.path.isdir(path):
        bad_surveys.append(survey)
    if bad_surveys:
        print("The following surveys do not exist:", ", ".join(bad_surveys))
        print("Please create them or remove them from SURVEYS before continuing")
        return 0
    return 1

def makeMetafields(survey):
    default = {"StartDate":0, "EndDate":1, 
                "Status":2, "IPAddress":3,
                "Progress":4, "Duration":5, 
                "Finished":6, "RecordedDate":7, 
                "ResponseID":8, "LocationLatitude":13, 
                "LocationLongitude":14,"UserLanguage":16}
    path = os.path.join("surveys", survey, "metafields.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(default, file, indent=4)