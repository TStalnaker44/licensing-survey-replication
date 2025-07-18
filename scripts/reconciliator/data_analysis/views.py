from django.shortcuts import render, redirect
from .scripts.settings import CONFIG
from .scripts.run_analysis import main as run_analysis
from .scripts.qualtrics_reader import makeQJSON
from .scripts.manage_invalid import getInvalidJSON, writeInvalid, getJSONtoQualtrics
from datetime import datetime
from global_vals import get_survey_internal, get_survey_display, has_csv
from django.core.exceptions import ValidationError
import os, json
import magic
from django.contrib import messages


def string_to_bool(s):
    return s.lower() == "true"

def updateInvalids(request):

    survey = get_survey_internal() #<-- It is this function that causes problems on reload and refresh
    invalid = getInvalidJSON(os.path.join("surveys", survey))
    invalid = {key:invalid[str(key)] for key in sorted([int(k) for k in invalid.keys()])}
    return render(request, 'update_invalids.html', {"invalid":invalid})


def configure_analysis(request):
    cur_survey = get_survey_display()

    return render(request, 'analysis_config.html', {"cur_survey": cur_survey})


def uploadQualtricsFile(request):
    cur_survey = get_survey_display()

    return render(request, 'qualtrics_upload.html', {"cur_survey": cur_survey})


def uploadDataFile(request):
    cur_survey = get_survey_display()

    return render(request, 'data_upload.html', {"cur_survey": cur_survey})


def reviewSurveyQuestions(request):
    survey = get_survey_internal()
    path = os.path.join("surveys", survey, "questions.json")
    with open(path, 'r', encoding="utf-8") as file:
        questions = json.load(file)
    for gname, gdata in questions.items():
        for qname, qdata in gdata.items():
            if qdata.get("options"):
                qdata["options"] = [i.replace("'", "&#39;") for i in qdata["options"]]
    return render(request, 'review_questions.html', {"questions": questions,
                                                        "question_types": CONFIG.QUESTION_TYPES,
                                                        "survey": survey})


def run_data_analysis(request):
    if request.method == 'POST':
        from_source = request.POST['from_source']
        pre_process = request.POST['pre_process']
        plot = "false" #request.POST['plot'] <-- TODO remove these files
        coding_done = request.POST['coding_done']

        CONFIG.set_survey(get_survey_internal())
        CONFIG.set_from_source(string_to_bool(from_source))
        CONFIG.set_pre_process(string_to_bool(pre_process))
        CONFIG.set_plot(string_to_bool(plot))
        CONFIG.set_response_coding_done(string_to_bool(coding_done))

        run_analysis()

        return render(request, 'analysis_complete.html')


def createQuestionsFile(request):
    if request.method == 'POST':
        if canGenerateJSON(request):
            return render(request, 'upload_success.html')
        else:
            return render(request, 'qualtrics_upload.html',
                          {"cur_survey": get_survey_display(), "error": "Error Uploading: File is not a QSF"})

def addInvalid(request):
    if request.method == 'POST':
        addition = request.POST["add_invalid"]
        if addition == "":
            return updateInvalids(request)
        else:
            addition = int(addition)
        reason = request.POST["add_explanation"] or "None given"
        invalid = json.loads(request.POST["list_data"])
        survey = get_survey_internal()
        mapping = getJSONtoQualtrics(survey)
        if not addition in mapping.keys():
            return None # <-- TODO
        else:
            if not str(addition) in invalid.keys(): # <-- This is a safe guard
                mapping = getJSONtoQualtrics(survey)
                invalid[addition] = {"qualtrics":mapping[addition], "reason":reason}
            writeInvalid(survey, invalid)
            return updateInvalids(request)

def removeInvalid(request):
    if request.method == 'POST':
        remove = request.POST["remove"]
        invalid = json.loads(request.POST["list_data2"])
        survey = get_survey_internal()
        invalid.pop(remove)
        writeInvalid(survey, invalid)
        return updateInvalids(request)

def canGenerateJSON(request):
    file = request.FILES['fileUpload']
    file_str = str(file)
    print(file_str[-4:])

    # Check for correct file type (qsf (essentially a JSON))
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file.read(1024))
    file.seek(0)  # Reset file pointer
    try:
        if not (mime_type == 'text/plain' and file_str[-4:] == '.qsf'):
            raise ValidationError('File is not a QSF.')
    except ValidationError as e:
        messages.error(request, str(e))
        return False

    try:
        file.seek(0)
        json.load(file)
    except json.JSONDecodeError:
        # print("Failure parsing")
        messages.error(request, "File is not a QSF.")
        return False
    finally:
        file.seek(0)

    new_file_name = get_survey_internal()
    path = os.path.join("surveys", new_file_name, "files", f"{new_file_name}.qsf")
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    makeQJSON(os.path.join("surveys", new_file_name))
    return True


def createDataFile(request):
    if request.method == 'POST':
        file = request.FILES['fileUpload']
        file_str = str(file)

        # Check for correct file type (CSV)
        # Check MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file.read(1024))
        file.seek(0)  # Reset file pointer
        csv_mime_types = ['text/csv', 'application/csv', 'application/vnd.ms-excel']
        try:
            if not (mime_type in csv_mime_types or (mime_type == 'text/plain' and file_str[-4:] == '.csv')):
                raise ValidationError('File is not a CSV.')
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'data_upload.html',
                          {"cur_survey": get_survey_display(), "error": "Error Uploading: File is not a CSV"})

        survey_name = get_survey_internal()
        now = datetime.now().strftime('%m-%d-%y')

        path = os.path.join("surveys", survey_name, "files", f"data_{now}.csv")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        data_was_uploaded = has_csv(get_survey_internal())
        return render(request, 'data_upload_success.html', {"data_was_uploaded": data_was_uploaded})


def updateSurveyQuestions(request):
    if request.method == 'POST':

        survey = get_survey_internal()

        path = os.path.join("surveys", survey, "questions.json")
        print(path)
        with open(path, 'r', encoding="utf-8") as file:
            questions = json.load(file)

        for block_name, block_data in questions.items():
            # To preserve question order, create a new dictionary and fill it as you go
            new_block = {}
            
            for qid, qdata in block_data.items():
                qdata['type'] = request.POST[f"{qid}_qtype"]
                if request.POST.get(f"{qid}_contains_pii"):
                    qdata['contains_pii'] = True
                if request.POST.get(f"{qid}_convert_to_range"):
                    qdata['convert_to_range'] = True
                if request.POST.get(f"{qid}_coded"):
                    qdata['coded'] = True
                    
                found_id = request.POST[f"{qid}_id"].strip()
                    
                if found_id != qid: # QID was changed
                    # Add qual_name field if it wasn't present
                    if "qual_name" not in qdata:
                        qdata["qual_name"] = qid
                    
                    new_block[found_id] = qdata
                else:
                    new_block[qid] = qdata
                    
                # print(new_block)
                    
            questions[block_name] = new_block

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(questions, file, ensure_ascii=False, indent=4)

        data_was_uploaded = has_csv(get_survey_internal())
        return render(request, 'data_upload_success.html', {"data_was_uploaded": data_was_uploaded})
