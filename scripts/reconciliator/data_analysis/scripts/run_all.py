from .csv2json import CSVConverter
from .sanitize import sanitize
from .json_converter import convert
from .partition import partition
from .plot import plot
from .settings import CONFIG
from .populate_database import populateDatabase  # Import the database population function

import os

from .results_json import ResultsJson


def main():
    survey = CONFIG.SURVEY

    survey_path = os.path.join("surveys", survey)
    print("Processing %s survey..." % (survey,))

    if CONFIG.PRE_PROCESS:

        if CONFIG.FROM_SOURCE:
            # Generate JSON Files from CSV
            CSVConverter(survey_path).convertCSV()

            # Sanitize JSON
            print("Sanitizing files...")
            sanitize(survey_path)

            # Populate the database
            print("Populating the database with sanitized data...")
            print(survey_path.split(os.path.sep)[-1])
            populateDatabase(survey_path.split(os.path.sep)[-1])

        # Make the data directory if it doesn't exist
        data_path = os.path.join(survey_path, "data")
        if not os.path.isdir(data_path):
            os.mkdir(data_path)

        ## Convert JSON to CSV
        print("Converting JSON to CSV...")
        convert(survey_path)

        if CONFIG.RESPONSE_CODING_DONE:
            ## Partition response coding
            print("Partitioning Response Coding Files...")
            partition(survey_path)

    ## Generate results.json
    ResultsJson().makeResultsJson()

    if CONFIG.PLOT:

        # Make the figs directory if it doesn't exist
        fig_path = os.path.join(survey_path, "figs")
        if not os.path.isdir(fig_path):
            os.mkdir(fig_path)

        ## Plot the results
        print("Plotting Results (this may take awhile)...")
        for ft in CONFIG.FILE_TYPES:
            print(f"Plotting {survey} survey as {ft}...")
            plot(survey_path, ft)

    print("All data processed!")
