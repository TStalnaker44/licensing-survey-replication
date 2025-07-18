
import csv, json, os, glob

class CSVConverter():

    # Preconditions: Has a survey folder with a files directory, questions.json, metafields.json, and a data file
    # surveyFolder should be of format surveys/{surveyName}
    def __init__(self, surveyFolder):
        self._base_path = os.path.join(surveyFolder, "files")
        self._survey_folder = surveyFolder
        self._question_blocks = self.getQuestionBlocks()
        self._metafields = self.getMetaFields()
        self._file_date = self.getDate()
        self._d = {}
        self._id_mapping = self.getJSONMapping()

    def getJSONMapping(self):
        path = os.path.join(self._survey_folder, "files", "id-mappings.json")
        if os.path.exists(path):
            with open(path) as file:
                return json.load(file)
        else:
            return {}

    def saveIDMapping(self):
        path = os.path.join(self._survey_folder, "files", "id-mappings.json")
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(self._id_mapping, file, indent=4)

    def getQuestionBlocks(self):
        path = os.path.join(self._survey_folder, "questions.json")
        with open(path) as file:
            return json.load(file)

    def getMetaFields(self):
        path = os.path.join(self._survey_folder, "metafields.json")
        with open(path) as file:
            return json.load(file)
        
    def extractMetaData(self, row):
        meta = {}
        for field, index in self._metafields.items():
            meta[field] = row[index]
        return meta
    
    def extractSectionData(self, row, index, column):

        for question_label, questions in self._question_blocks.items():
            sec = {}
            
            for qname, qdata in questions.items():
                qid = qdata.get("qual_name", qname)
                
                qtype = qdata["type"]
                if qtype in ("single-select", "single-text", "likert", "short-answer", "email", "slider"):
                    sec[qid] = row[column]
                    column += 1
                elif qtype in ("multi-select"):
                    sec[qid] = row[column].split(",")
                    column += 1
                elif qtype == "single-select-with-other":
                    sec[qid] = {"answers":row[column], "other":row[column+1]}
                    column += 2
                elif qtype == "multi-select-with-other":
                    sec[qid] = {"answers":self.getLabels(row[column]), "other":row[column+1]}
                    column += 2
                elif qtype in ("ranked", "constant-sum", "matrix", "matrix-with-other"):
                    options = qdata.get("options", None)
                    if options == None: raise ValueError("Questions of type 'ranked' require 'options' field")
                    sec[qid] = {i+1:row[column+i] for i in range(len(options))}
                    column += len(options)
                elif qtype in ("ranked-with-other", "constant-sum-with-other"):
                    options = qdata.get("options", None)
                    if options == None: raise ValueError("Questions of type 'ranked-with-other' require 'options' field")
                    sec[qid] = {i+1:row[column+i] for i in range(len(options))}
                    sec[qid]["other"] = row[column+len(options)]
                    column += len(options) + 1
                else:
                    raise ValueError(f"Unknown qtype: {qtype}")
                
            self._d[index][question_label] = sec
            
        return column
    
    def getDate(self):
        path = os.path.join(self._base_path, "data_*.csv")
        return glob.glob(path)[-1].split(os.sep)[-1].replace("data_", "").replace(".csv","")
    
    def writeJSON(self):
        survey_name = self._survey_folder.split(os.sep)[1]
        file_name = os.path.join(self._base_path, f"{survey_name}_completers_{self._file_date}.json")
        with open(file_name, "w") as file:
            json.dump(self._d, file, indent=4)

    def getLabels(self, temp):
        temp = temp.replace(", ", "||")
        return [t.replace("||", ", ") for t in temp.split(",")]

    def getJSONID(self, row):
        qualID_index = self._metafields["ResponseID"]
        qualID = row[qualID_index]
        if not qualID in self._id_mapping:
            index = len(self._id_mapping.keys())
            self._id_mapping[qualID] = index
        return self._id_mapping[qualID]
    
    def processRow(self, row):
        index = self.getJSONID(row)
        self._d[index] = {"meta":self.extractMetaData(row)}
        self.extractSectionData(row, index, len(self._metafields)-1)

    def convertCSV(self):
        
        path = os.path.join(self._base_path, f"data_{self._file_date}.csv")
        
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            
            for i, row in enumerate(reader):
                # The first 3 rows of the .csv file are the header
                not_header = i > 2
                if not_header:
                    # index = i - 3 # Start indexing at 0 (skip header rows)
                    progress_index = self._metafields["Progress"]
                    incomplete = int(row[progress_index]) != 100
                    if not incomplete:
                        self.processRow(row)
                        
        self.writeJSON()
        self.saveIDMapping()

                    


