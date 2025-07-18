import requests, csv, openpyxl, shutil, os

SPREADSHEET_ID = "1pkF41QnvW6rmfpVNf77gXJRioDTRYkvIBtmEfjXYKIo"


class CodeBook():
    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls._CodeBook()
        return cls._INSTANCE

    class _CodeBook():
        def __init__(self):
            self.updateCodes()

        def updateCodes(self):
            self.loadCodeBook()
            self.codes = self.getCodes()
            self.addDefinitions()

        def filterCodes(self, codes):
            new_codes = []
            for code, definition in codes.items():
                if code != "" and not code.startswith("--"):
                    if definition == "":
                        definition = "No definition available. Try downloading latest code book."
                    new_codes.append((code, definition))
            new_codes.sort(key=lambda x: x[0])
            return new_codes

        def get(self, qid):
            return self.filterCodes(self.codes[qid])

        def getQuetions(self):
            return list(self.codes.keys())

        def search(self, term, qid):
            term = term.lower()
            hits = {}
            codes = self.codes[qid]
            for code, definition in codes.items():
                if term in code.lower() or term in definition.lower():
                    definition = definition.replace("&#39;", "'")
                    hits[code] = definition
            return hits

        def loadCodeBook(self):
            spreadsheet_id = SPREADSHEET_ID  # "18NPTcOH8y9ghX6Plxgt05Nm3CnpQyl1v9N6Ah311shc"
            sheet_name = "Selection Options"
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            response = requests.get(url)
            if response.status_code == 200:
                with open("downloaded_sheet.csv", "wb") as file:
                    file.write(response.content)
            else:
                print(f"Failed to download CSV. Status code: {response.status_code}")

        def convertXLSXtoCSV(self):
            path = "downloaded_sheet.xlsx"
            workbook = openpyxl.load_workbook(path)
            sheet = workbook['Selection Options']
            with open("downloaded_sheet.csv", "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                for row in sheet.iter_rows(values_only=True):
                    writer.writerow(row)

        def getCodes(self):
            if not os.path.exists("downloaded_sheet.csv"):
                print("Warning: downloaded_sheet.csv not found.")
                return {}

            with open("downloaded_sheet.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                codes = {}
                for i, row in enumerate(reader):
                    if i == 0:
                        questions = row
                        for column in row:
                            if column != "": codes[column] = {}
                    else:
                        for j, column in enumerate(row):
                            if column != "":
                                codes[questions[j]][column] = ""
                return codes

        def addDefinitions(self):
            path = "downloaded_sheet.xlsx"

            if not os.path.exists(path):
                print("downloaded_sheet.xlsx does not exist")
                return self.codes

            workbook = openpyxl.load_workbook(path)
            sheet = workbook['Selection Options']

            def getDefinition(comment):
                if comment is None:
                    return ("", "")
                else:
                    comment = comment.text.split('\n\t-')
                    return (comment[0], comment[-1])

            questions = self.getQuetions()
            # Iterate over columns
            for i, column in enumerate(sheet.iter_cols(min_col=1, max_col=len(questions), min_row=3)):
                for cell in column:
                    term = cell.value
                    definition, author = getDefinition(cell.comment)
                    if term != None:
                        definition = definition.replace("'", "&#39;")
                        self.codes[questions[i]][term] = definition
            return self.codes


CODES = CodeBook.instance()
