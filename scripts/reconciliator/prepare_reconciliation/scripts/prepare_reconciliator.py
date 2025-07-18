
"""
- Complete steps 0-3 to set up The Grand Reconciliator (move database to reconciliator/reconciliator)
- Reconcile the codes
- Then run step 4
"""
import os
from .comparer import main as comparer
from .to_json import main as to_json
from .pull_comments import main as pull_comments
from .createDB import main as createDB
from .populateDB import main as populateDB
from .resp_config import REC_CONFIG

def main():
    ## The questions.json needs to be updated with the 'coded' attributes-- todo: make this automatic
    createGeneratedFilesFolder()
    comparer()
    to_json()
    pull_comments()
    createDB()
    populateDB()

def createGeneratedFilesFolder():
    path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files")
    if not os.path.exists(path):
        os.makedirs(path)