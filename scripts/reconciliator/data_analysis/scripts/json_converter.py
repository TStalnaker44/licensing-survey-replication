import os, glob, importlib
from .converter import Converter

def getMostRecent(survey):
    path = os.path.join(survey, "files", "*sanitized_*.json")
    return glob.glob(path)[-1].split(os.sep)[-1]

def convert(survey):
    file_name = getMostRecent(survey)
    conv = Converter(survey, file_name)
    conv.main()