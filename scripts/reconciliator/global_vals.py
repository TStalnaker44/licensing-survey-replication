# Store any values that are needed by multiple pages
import json, os

global cur_survey_internal
global cur_survey_display
global cur_coder

cur_survey_internal, cur_survey_display = None, None
cur_coder = None

def set_survey(survey):
    global cur_survey_internal
    global cur_survey_display
    
    if survey != None:
        cur_survey = format_internal_name(survey) #Ensure correct format for internal name
        found = False
        for root, dirs, files in os.walk("surveys/" + cur_survey):
            if "survey_metadata.json" in files:
                found = True
                with open(os.path.join(root,"survey_metadata.json"), 'r') as file:
                    survey_metadata = json.load(file)
                cur_survey_internal = survey_metadata.get('name_internal')
                cur_survey_display = survey_metadata.get('name_display')
        if not found:
            print("no metadata file found")
    else:
        cur_survey_internal, cur_survey_display = None, None

def get_survey_internal():
    return cur_survey_internal

def get_survey_display():
    return cur_survey_display

formatted_name = ""

def format_internal_name(survey_name):
    formatted_name = survey_name
    formatted_name = formatted_name.replace(" ", "_")
    formatted_name = formatted_name.replace("\\", "&#92;")
    formatted_name = formatted_name.replace("[", "&#91;")
    formatted_name = formatted_name.replace("]", "&#93;")
    formatted_name = formatted_name.replace("/", "&#47;")
    formatted_name = formatted_name.replace(":", "&#58;")
    formatted_name = formatted_name.replace("*", "&#42;")
    formatted_name = formatted_name.replace("?", "&#63;")
    formatted_name = formatted_name.replace("\"", "&#34;")
    formatted_name = formatted_name.replace("<", "&#60;")
    formatted_name = formatted_name.replace(">", "&#62;")
    formatted_name = formatted_name.replace("|", "&#124;")
    formatted_name = formatted_name.lower()
    return formatted_name

def format_display_name(survey_name):
    formatted_name = survey_name
    formatted_name = formatted_name.replace("_", " ")
    formatted_name = formatted_name.replace("&#92;", "\\")
    formatted_name = formatted_name.replace("&#91;", "[")
    formatted_name = formatted_name.replace("&#93;", "]")
    formatted_name = formatted_name.replace("&#47;", "/")
    formatted_name = formatted_name.replace("&#58;", ":")
    formatted_name = formatted_name.replace("&#42;", "*")
    formatted_name = formatted_name.replace("&#63;", "?")
    formatted_name = formatted_name.replace("&#34;", "\"")
    formatted_name = formatted_name.replace("&#60;", "<")
    formatted_name = formatted_name.replace("&#62;", ">")
    formatted_name = formatted_name.replace("&#124;", "|")
    formatted_name = formatted_name.title()
    return formatted_name


def set_coder(coder):
    global cur_coder
    if coder != None:
        cur_coder = coder
    else:
        cur_coder = None

def get_coder():
    return cur_coder
    
# Returns true if survey has a csv file in the survey files folder, otherwise returns false 
def has_csv(survey_internal_name):
    if not survey_internal_name:
        print("Cannot find csv files for non-existing survey: " + survey_internal_name)
        return False
    
    for file in os.listdir(os.path.join("surveys", survey_internal_name, "files")):
        if file.endswith(".csv"):
            return True
    return False

