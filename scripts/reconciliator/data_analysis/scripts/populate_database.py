import os
import json
import sqlite3
import glob
import time
from random import random
from sqlite3 import DatabaseError

from app.models import Respondent, Response, Question, Survey
from .results_json import getQIDMapping


def getFilePath(directory):
    """
    Get the path to the 'files' subdirectory in the given directory.
    """
    return os.path.join("surveys", directory, "files")


def getLatestSanitizedFile(directory):
    """
    Fetch the latest sanitized file from the surveys directory.
    """
    path = os.path.join(getFilePath(directory), "*sanitized_*.json")
    files = glob.glob(path)
    if not files:
        raise FileNotFoundError("No sanitized files found in the directory.")
    files = sorted([f.split(os.sep)[-1][:-5] for f in files])
    return os.path.join(getFilePath(directory), files[-1] + ".json")


def loadSanitizedJSON(directory):
    """
    Load the latest sanitized JSON file.
    """
    path = getLatestSanitizedFile(directory)
    print(f"Loading sanitized data from {path}...")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def populateDatabase(survey_internal):
    """
    Populates the SQLite database with respondents, questions, and responses
    from the latest sanitized file.
    """
    try:
        # Load sanitized data
        data = loadSanitizedJSON(survey_internal)

        # Get the survey from the database
        survey = Survey.objects.get(internal_id=survey_internal)
        # Delete all relational data
        survey.questions.all().delete()
        survey.respondents.all().delete()

        # Prepare mappings for question IDs to avoid duplicates
        question_ids = {}

        print("Populating database...")
        # Insert respondents, questions, and responses
        for response_id, response_data in data.items():
            meta = response_data["meta"]
            qualtrics_id = meta["ResponseID"]

            # Insert respondent into respondents table
            respondent = Respondent(survey_id=survey.id, qualtrics_id=qualtrics_id)
            respondent.save()

            # Insert questions and responses
            for block_name, block_data in response_data.items():
                if block_name == "meta":
                    continue  # Skip metadata

                for question, response in block_data.items():
                    # Add question to app_question if not already present
                    if question not in question_ids:
                        db_question = Question(question=question, survey_id=survey.id)
                        db_question.save()
                        question_ids[question] = db_question.id

                    # Insert response into responses table
                    response = Response(json_id=response_id, response=response,
                                        question_id=question_ids[question], respondent_id=respondent.id)
                    response.save()



    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Database operation completed.")
