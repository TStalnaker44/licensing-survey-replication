from django.shortcuts import render
import global_vals as gv
import os, json

from app.models import Survey
from data_analysis.views import canGenerateJSON
import shutil


# Returns a list of survey directories in the surveys folder
def get_survey_dirs():
    return [s for s in os.listdir("surveys") if os.path.isdir(os.path.join("surveys", s))]


def index(request):
    # Create the surveys directory if it does not exist
    if not os.path.exists("surveys"):
        os.mkdir("surveys")

    # Filter out .gitignore
    surveys = [gv.format_display_name(survey) for survey in get_survey_dirs()]

    if request.method == 'POST':
        cur_survey = request.POST.get("select_survey")
        gv.set_survey(cur_survey)
    elif request.method == 'GET':
        # Ensure that all surveys in directory have survey_metadata.json file
        for sur in get_survey_dirs():
            path = os.path.join("surveys", sur)
            if (os.path.exists(path) and not os.path.exists(os.path.join(path, "survey_metadata.json"))):
                names = {
                    "name_internal": sur,
                    "name_display": gv.format_display_name(sur)
                }
                with open(os.path.join(path, "survey_metadata.json"), "w", encoding="utf-8") as file:
                    json.dump(names, file, indent=4)

        # Set survey
        cur_survey = gv.get_survey_internal()
        if (surveys and cur_survey is None):
            # Set survey as display name not internal name 
            cur_survey = surveys[0]
            gv.set_survey(cur_survey)
        elif not (surveys):
            gv.set_survey(None)
    cur_survey = gv.get_survey_display()

    if (cur_survey is None):
        return render(request, "no_survey_home.html")
    else:
        csv_exists = gv.has_csv(gv.get_survey_internal())
        return render(request, 'home.html', {"surveys": surveys, "cur_survey": cur_survey, "csv_exists": csv_exists})


def addUploadSurveyForm(request):
    return render(request, "add_upload_survey.html")


def add_upload_survey(request):
    if request.method == 'POST':
        # Add survey

        # Remove trailing and leading spaces
        survey = request.POST.get("new_survey").strip().replace(" ", "_")

        # If the survey name is empty, render the special failure page instead
        if survey == "":
            return render(request, "failure_empty.html")

        survey_internal = gv.format_internal_name(survey)

        names = {
            "name_internal": survey_internal,
            "name_display": survey.replace("_", " ").title()
        }

        # Code for adding new survey and directory structure
        path = os.path.join("surveys", survey_internal)

        # Track the old survey name
        old_survey_name = gv.get_survey_display()

        # Add the newly created survey to the open-coding database
        db_survey = Survey(internal_id=survey_internal)
        db_survey.save()

        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(os.path.join(path, "files"))
            os.makedirs(os.path.join(path, "data"))
            os.makedirs(os.path.join(path, "figs"))
            os.makedirs(os.path.join(path, "coders"))
            with open(os.path.join(path, "survey_metadata.json"), "w", encoding="utf-8") as file:
                json.dump(names, file, indent=4)
            gv.set_survey(survey)
        else:
            return render(request, "add_upload_survey_failure.html",
                          {"survey": gv.format_display_name(survey_internal)})

        if canGenerateJSON(request):
            return render(request, 'add_upload_survey_success.html', {"survey": gv.get_survey_display()})
        else:
            # Reset the survey name
            gv.set_survey(old_survey_name)

            # Delete survey that was created
            path = os.path.join("surveys", survey_internal)
            if os.path.exists(path):
                shutil.rmtree(path)
            return render(request, 'add_upload_survey.html', {"error": "Error Uploading: File is not a QSF"})


def removeSurveyForm(request):
    surveys = [gv.format_display_name(s) for s in get_survey_dirs()]
    # gv.set_survey(None)

    return render(request, "remove_survey.html", {"surveys": surveys})


def remove_survey(request):
    survey = gv.get_survey_internal()

    # If the survey name is empty or None, render the special failure page instead
    if survey is None or survey == "":
        return render(request, "remove_failure.html")

    # Code for the survey path to remove
    path = os.path.join("surveys", survey.strip())

    if os.path.exists(path):
        # Delete survey and all of its files
        shutil.rmtree(path)

        # Remove the survey from the database
        Survey.objects.filter(internal_id=survey.strip()).delete()

        # Update the current survey
        valid = [s for s in get_survey_dirs() if s != survey]

        if len(valid) == 0:
            gv.set_survey(None)
        else:
            gv.set_survey(valid[0])

        return index(request)
    else:
        return render(request, "remove_failure.html", {"survey": gv.format_display_name(survey)})
