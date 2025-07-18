
import json, sqlite3, os, glob
from .utils import all_combinations
from .resp_config import REC_CONFIG

INPUT_FILE = "response_codes.json"

insert_questions = "INSERT INTO questions (qid, text) VALUES (?,?)"

insert_responses = "INSERT INTO responses (pid, qid, response) VALUES (?,?,?)"

insert_terms = "INSERT INTO terms (term, definition, qid) VALUES (?,?,?)"

insert_response_codes = "INSERT INTO response_codes (pid, qid, coder_combo, codes) VALUES (?,?,?,?)"

insert_coders = "INSERT INTO coders (label) VALUES (?)"
            
def getDataFromFile(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
    
def getQuestionsData():
    path = os.path.join("surveys", REC_CONFIG.SURVEY, "questions.json")
    return getDataFromFile(path)
        
def getResponseCodeData(q, pid, d):
    data = []
    codes = d[q][pid]
    for label in all_combinations([f"R{i}" for i in range(REC_CONFIG.CODERS)]):
        data.append((label, " ".join(codes[label])))
    return data

def insertIntoDB(data, conn, query):
    cursor = conn.cursor()
    cursor.execute(query, data)

def addResponseCodesToDB(conn):
    path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", INPUT_FILE)
    d = getDataFromFile(path)
    for question in d:
        for response_id in d[question]:
            data = getResponseCodeData(question, response_id, d)
            for datum in data:
                datum = (response_id, question, datum[0], datum[1])
                insertIntoDB(datum, conn, insert_response_codes)
    conn.commit()

def addQuestionsToDB(conn):
    d = getQuestionsData()
    for group in d.values():
        for qname, qdata in group.items():
            data = (qname, qdata["question"])
            insertIntoDB(data, conn, insert_questions)
    conn.commit()

def addCodersToDB(conn):
    for label in all_combinations([f"R{i}" for i in range(REC_CONFIG.CODERS)]):
        insertIntoDB((label,), conn, insert_coders)
    conn.commit()

def getResponseData(d):
    questions = getQuestionsData()
    coded_questions = []
    for gname, gdata in questions.items():
        for qname, qdata in gdata.items():
            if qdata.get("coded"):
                coded_questions.append((gname, qname))
    responses = []
    for pid in d:
        for g, q in coded_questions:
            responses.append((int(pid), q, d[pid][g][q]))
    return responses

def getMostRecentData():
    path = os.path.join("surveys", REC_CONFIG.SURVEY, "files", "*sanitized_*.json")
    return glob.glob(path)[-1].split(os.sep)[-1]
        
def addResponsesToDB(conn):
    path = os.path.join("surveys", REC_CONFIG.SURVEY, "files", getMostRecentData())
    d = getDataFromFile(path)
    for response in getResponseData(d):
        insertIntoDB(response, conn, insert_responses)
    conn.commit()

def addTermsToDB(conn):
    path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", "glossary.json")
    d = getDataFromFile(path)
    for qid in d:
        for term in d[qid]:
            data = (term, d[qid][term], qid)
            insertIntoDB(data, conn, insert_terms)
    conn.commit()

def main():
    path = REC_CONFIG.DB_PATH
    conn = sqlite3.connect(path)
    addQuestionsToDB(conn)
    addResponsesToDB(conn)
    addResponseCodesToDB(conn)
    addTermsToDB(conn)
    addCodersToDB(conn)
    conn.close()

if __name__ == "__main__":
    main()
