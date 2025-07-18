from django.shortcuts import render
import os
from .scripts.resp_config import REC_CONFIG
from .scripts import prepare_reconciliator
from .scripts import reconcile
from global_vals import get_survey_internal, get_survey_display

def prepare_reconciliation(request):
    surveys = os.listdir("surveys")
    surveys = [s.title() for s in surveys]

    cur_survey = get_survey_display()
    return render(request, 'prepare_reconciliation.html',
                  {"surveys": surveys, "cur_survey":cur_survey})

def applyReconciliation(request):
    surveys = os.listdir("surveys")
    surveys = [s.title() for s in surveys]

    cur_survey = get_survey_display()
    return render(request, 'apply_reconciliation.html', {"surveys": surveys, "cur_survey":cur_survey})

def uploadCoderFile(request):

    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]

    cur_survey = get_survey_display()
    return render(request, 'upload_coder_file.html', {"surveys": surveys, "cur_survey":cur_survey})

def run_reconciliation(request):
    if request.method == 'POST':
        survey_name = get_survey_internal()
        REC_CONFIG.set_survey(survey_name)

        file = request.FILES.get('fileUpload')
        path = os.path.join("surveys", survey_name, "response_coding", 
                                "code_files", "reconciliation.csv")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        reconcile.main()

        return render(request, 'reconciliation_complete.html')

def run_preparation(request):
    if request.method == 'POST':
        coder_count = request.POST['quantity']
        file = request.FILES.get('fileUpload')
        survey_name = get_survey_internal()
        REC_CONFIG.set_survey(survey_name)
        REC_CONFIG.set_coders(int(coder_count))
        if file:
            path = os.path.join("surveys", survey_name, "response_coding", 
                                "code_files", "dictionary.xlsx")
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        prepare_reconciliator.main()
        return render(request, 'preparation_complete.html')
    
def createCoderFile(request):

    if request.method == 'POST':
        file = request.FILES['fileUpload']
        survey_name = get_survey_internal()
        coder = request.POST['coder']

        coding_dir = os.path.join("surveys", survey_name, "response_coding")
        if not os.path.exists(coding_dir):
            os.makedirs(coding_dir)
        code_files_dir = os.path.join(coding_dir, "code_files")
        if not os.path.exists(code_files_dir):
            os.makedirs(code_files_dir)

        path = os.path.join(code_files_dir, f"coder_{coder}.csv")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return render(request, 'coder_upload_success.html')

