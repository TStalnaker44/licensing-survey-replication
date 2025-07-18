import os
import json
import glob
from django.shortcuts import render, redirect
from django.urls import reverse
from .scripts.utils import CODES
import global_vals as gv

FOLDERS = {"initial": "initial_survey"}

# This function resolves the folder path for a survey
def survey2folder(survey):

    if survey in FOLDERS:
        folder = FOLDERS[survey]
    else:
        folder = survey  # If not in FOLDERS, just use the survey name as the folder name
    folder = os.path.join(folder)
    return folder.replace(" ", "_")

# Function to get the file path for the questions.json file for a given survey
def getQuestionsJsonPath(survey):
    # Get the directory of the current script (open_coding.py)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the absolute path to the questions.json file
    base_path = os.path.abspath(os.path.join(current_script_dir, '..', '..', '..', 'surveys'))
    folder = survey2folder(survey)  # Resolve the survey folder
    questions_json_path = os.path.join(base_path, folder, 'questions.json')
    
    # Check if the file exists
    if not os.path.exists(questions_json_path):
        raise FileNotFoundError(f"questions.json not found for survey '{survey}' at {questions_json_path}")
    
    return questions_json_path

# Function to get available surveys by reading the surveys directory
def getAvailableSurveys():
    surveys = []
    # Assuming surveys are at the same level as scripts/reconciliator/
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'surveys'))
    
    # Iterate over the directories inside the surveys folder
    for survey in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, survey)):  # Only consider directories
            surveys.append(survey.replace("_", " "))  # Replace underscores with spaces for readability
    return surveys

# Function to get the most recent sanitized data file for a given survey
def getMostRecentData(survey):
    folder = survey2folder(survey)  # Resolve the survey folder
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'surveys', folder))
    path = os.path.join(base_path, "files", "*sanitized_*.json")

    # Get the most recent sanitized file (latest by name)
    files = glob.glob(path)
    if not files:
        raise FileNotFoundError(f"No sanitized JSON files found in {path}")
    return files[-1].split(os.sep)[-1]  # Return only the file name

# Function to load the most recent response data for a given survey
def getResponseData(survey):
    folder = survey2folder(survey)  # Resolve the survey folder
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'surveys', folder))
    path = os.path.join(base_path, "files", getMostRecentData(survey))
    
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def getValidQuestions(survey):
    # Retrieve the path to questions.json using the previously defined method
    path = getQuestionsJsonPath(survey)
    
    with open(path, "r", encoding="utf-8") as file:
        d = json.load(file)
    
    # Extract and return valid questions with their IDs and question text
    questions = []
    for group_content in d.values():  # Iterate through the groups (e.g., "Scales")
        for q_name, question_content in group_content.items():
            # Append a tuple of (question_id, question_text)
            if question_content["type"] in ["single-text", "short-answer"]:
                questions.append((q_name, question_content["question"]))
    return questions
# Function to get valid Participant IDs from the response data
def getValidPIDs(response_data):
    return sorted([int(k) for k in response_data.keys()])

#Function to add a new code to the codebook (JSON file)
def addCode(request, base_path):
    # if request.method == 'POST':
    code_name = request.POST.get('code_name')
    description = request.POST.get('code_description')
    question_id = request.POST.get('question_id')
    
    codebook_path = os.path.join(base_path, "codebook.json")

    # Read existing data or create an empty dictionary
    if os.path.exists(codebook_path):
        with open(codebook_path, 'r') as file:
            codebook = json.load(file)
    else:
        codebook = {}
    
    # Update the codebook
    if question_id not in codebook:
        codebook[question_id] = {}
    codebook[question_id][code_name] = description
    
    # Write the updated codebook back to the file
    with open(codebook_path, 'w') as file:
        json.dump(codebook, file, indent=2)

#Function to load in the codes from the codebook (JSON file) 
def loadCodes(base_path):
    codebook_path = os.path.join(base_path, "codebook.json")

    if os.path.exists(codebook_path):
        with open(codebook_path, 'r') as file:
            return json.load(file)
        
    return {}

def parse_responses_from_file(survey):

    data = getResponseData(survey)

    # List to store parsed responses
    parsed_responses = []

    # Iterate through each response in the data (0, 1, 2, 3, ...)
    for response_key, response_data in data.items():
        # Extract the Response ID from the "meta" data
        response_id = response_data["meta"]["ResponseID"]
        
        # Now we need to iterate through each block (e.g., "Default Question Block", "Block 1", etc.)
        for block_name, block_data in response_data.items():
            # Skip the "meta" block because it doesn't contain any questions/answers
            if block_name == "meta":
                continue
            
            # Now we iterate through each question in the block
            for question_id, response_text in block_data.items():
                # Append a dictionary with the question id, response id, and the response text
                parsed_responses.append({
                    "question_id": question_id,
                    "response_id": response_id,
                    "response": response_text
                })
    
    return parsed_responses

def open_coding(request):  
    surveys = getAvailableSurveys()
    selected_survey = gv.get_survey_internal()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'surveys', selected_survey))

    response_data = {}
    valid_questions = {}
    
    response_data = parse_responses_from_file(selected_survey)
    valid_questions = getValidQuestions(selected_survey)

    coder = gv.get_coder()

    if request.method == 'POST':
        addCode(request, base_path)

    codes = loadCodes(base_path)

    # Organize responses without using defaultdict
    organized_responses = {}
    for entry in response_data:
        question_id = entry['question_id']
        response_id = entry['response_id']
        response_text = entry['response']
        
        # Initialize nested dictionaries if they do not exist
        if question_id not in organized_responses:
            organized_responses[question_id] = {}
        if response_id not in organized_responses[question_id]:
            organized_responses[question_id][response_id] = []
        
        # Append the response text to the list for the given question and participant
        organized_responses[question_id][response_id].append(response_text)

    return render(request, 'open_coding.html', {
        'surveys': surveys,
        'selected_survey': selected_survey,
        'response_data': organized_responses,
        'valid_questions': valid_questions,
        'codes': codes,
        'coder': coder
    })