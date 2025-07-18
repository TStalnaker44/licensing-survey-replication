
import os

class Reconciliation_Config():

    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls._Config()
        return cls._INSTANCE
    
    class _Config():
        def __init__(self):
            self.CODERS = 2
            self.DB_NAME = "reconcile.db"
            self.DB_PATH = os.path.join("scripts", "reconciliator", self.DB_NAME)
            self.SURVEY = ""
            self.PATH = ""

        def set_coders(self, coders):
            self.CODERS = coders

        def set_survey(self, survey):
            self.SURVEY = survey
            self.PATH = os.path.join("surveys", survey)

REC_CONFIG = Reconciliation_Config.instance()