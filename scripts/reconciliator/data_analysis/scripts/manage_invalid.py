
import os, json

def writeInvalid(directory, invalids):
    path = os.path.join("surveys", directory, "files", "invalid.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(invalids, file)

def getJSONtoQualtrics(survey):
    path = os.path.join("surveys", survey, "files", "id-mappings.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return {value:key for key, value in data.items()}

def getInvalidJSON(directory):
    path = os.path.join(directory, "files", "invalid.json")
    if os.path.isfile(path): 
        with open(path, "r", encoding="utf-8") as file:    
            return json.load(file)
    else: 
        return {}

def readInvalid(directory):
    path = os.path.join(directory, "files", "invalid.json")
    if os.path.isfile(path): 
        with open(path, "r") as file:    
            return set([pid.strip() for pid in json.load(file).keys()])
    else: 
        return set()


"""
Here is the format of the proposed invalid file
0:{
    "qualtrics": "R_xxxxxxxxxxxx",
    "reason": "<explanation here>"
}
"""