from django.shortcuts import render
from .scripts.utils import Browser

# Create your views here.
def browse(request):
    qid = request.GET.get("qid", None)
    code = request.GET.get("code", None)
    b = Browser()
    questions = b.getQIDs()
    if not qid:
        qid = list(questions.keys())[0]
    codes = b.getCodes(qid)
    if not code:
        code = codes[0][0]
    responses = b.getResponses(qid, code)
    return render(request, 'browse.html', {"questions":questions,
                                           "codes":codes,
                                           "responses":responses,
                                           "qid":qid,
                                           "code":code})