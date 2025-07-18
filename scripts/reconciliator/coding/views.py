import os
from django.shortcuts import render, redirect
from django.urls import reverse
from .scripts.utils import CODES
from django.http import JsonResponse
from global_vals import get_survey_internal, set_coder, get_coder

# Create your views here.
def chooseCodes(request):
    if request.method == "GET":
        qid = request.GET.get("qid") or CODES.getQuetions()[0]
        codes = CODES.get(qid)
        questions = CODES.getQuetions()
        return render(request, 'choose_codes.html', {"codes":codes,
                                                    "questions":questions,
                                                    "qid":qid})
    if request.method == 'POST':
        file = request.FILES['fileUpload']
        qid = request.POST["qid"]
        path = os.path.join("downloaded_sheet.xlsx")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        CODES.convertXLSXtoCSV()
        CODES.updateCodes()
        return redirect(reverse('chooseCodes') + "?qid=" + qid)

def reloadCodes(request):
    CODES.updateCodes()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def searchCodes(request, question_id, term):
        hits = CODES.search(term, question_id)
        return render(request, "search_results.html", {"hits":hits})

def selectCoder(request):
    path = os.path.join("surveys", get_survey_internal(), "coders")
    if request.method == 'POST':
        cur_coder = request.POST.get("select_coder")
        set_coder(cur_coder)
        return redirect("open_coding")
    
    elif request.method == 'GET':
        if len(os.listdir(path)) == 0:
            createCoderDir()

    coders = [c for c in os.listdir(path)]
    if get_coder() is None and coders:
        set_coder(coders[0])
    return render(request, "select_coder.html", {"coders": coders})

def addCoder(request):
    if request.method == "POST":
        createCoderDir()
        path = os.path.join("surveys", get_survey_internal(), "coders")
        coders = [c for c in os.listdir(path)]
        return render(request, "select_coder.html", {"coders": coders})
        
def createCoderDir():
    path = os.path.join("surveys", get_survey_internal(), "coders")
    coderId = len(os.listdir(path))
    coderPath = "coder"+ str(coderId + 1)
    os.makedirs(os.path.join(path, coderPath))
    set_coder(coderPath)

