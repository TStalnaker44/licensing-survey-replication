
from app.models import *
import colorsys

def getQuestions():
    selections = Terms.objects.values("qid").distinct()
    return [x["qid"] for x in selections]

def getTerms(question):
    terms = Terms.objects.filter(qid=question)
    return terms.order_by("term")

def getResponse(qid, pid):
    response = Responses.objects.filter(qid=qid).filter(pid=pid)
    if len(response) > 0:
        return response[0]
    return []

def getQuestionText(question):
    return Questions.objects.get(qid=question).text

def getCodes(qid, pid):
    codings = ResponseCodes.objects.filter(qid=qid).filter(pid=pid)
    if len(codings) > 0:
        return {f"codes_{coding.coder_combo.lower()}":coding.codes.split() 
                for coding in codings}
    return None

def getValidPids(qid):
    pids = ResponseCodes.objects.filter(qid=qid)
    pids = pids.filter(codes__isnull=False).exclude(codes='').values("pid").distinct()
    return [x["pid"] for x in pids]

def getCoderLabels(codes):
    coder_labels = {}
    for key in codes:
        coders = list(filter(lambda x: x != "", key.split("_")[-1].split("r")))
        retstring = "Coder "
        for i, c in enumerate(coders):
            retstring += f"{int(c)+1}"
            if i < len (coders) - 2:
                retstring += ", "
            if i == len(coders) - 2:
                retstring += " & "
        coder_labels[key] = retstring
    return coder_labels

def getCoderColors(codes):
    # Trivial case:
    if len(codes) == 1: colors = ["white"]
    # Case for 2 coders
    elif len(codes) == 3: colors = ["yellow","lightcoral","white"]
    # Case for 3 coders
    elif len(codes) == 7: colors = ["yellow","lightcoral","lightblue","orange",
                                  "lightgreen","violet","white"]
    # The general case
    else: colors = get_distinct_colors(len(codes)-1) + ["white"]
    return {c:color for c, color in zip(codes.keys(), colors)}



def get_distinct_colors(n):
    colors = []

    for i in range(n):
        hue = i / n
        lightness = 0.5  # Can adjust to have lighter/darker colors
        saturation = 0.8  # Can adjust to have less/more saturated colors

        # Convert HSL color to RGB
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

        # Convert RGB color to hexadecimal
        color = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

        colors.append(color)

    return colors


def getDefinition(term, qid):
    terms = Terms.objects.filter(qid=qid).filter(term=term)
    if len(terms) > 0:
        return terms[0].definition
    else:
        return "TERM NOT IN DICTIONARY"
