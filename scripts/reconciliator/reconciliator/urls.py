"""reconciliator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import app.views
import coding.open_coding
import prepare_reconciliation.views
import home.views
import data_analysis.views
import coding.open_coding
import coding.views
import plot.views
import data_browser.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home.views.index, name="home"),
    path('reconciliator/', app.views.index, name='reconciliator'),
    path('glossary', app.views.dictionaryPage),
    path('update-content/', app.views.update_content, name="update_content"),
    path('get_popup_content/<str:question_id>/<str:content_id>/', app.views.get_popup_content, name='get_popup_content'),
    path('prepare_reconciliation/', prepare_reconciliation.views.prepare_reconciliation, name='prepare_reconciliation'),
    path('run_preparation/', prepare_reconciliation.views.run_preparation, name='run_preparation'),
    path('configure_analysis/', data_analysis.views.configure_analysis, name='configure_analysis'),
    path('run_data_analysis/', data_analysis.views.run_data_analysis, name='run_data_analysis'),
    path('uploadQualtricsFile/', data_analysis.views.uploadQualtricsFile, name='uploadQualtricsFile'),
    path('addUploadSurveyForm/', home.views.addUploadSurveyForm, name = "addUploadSurveyForm"),
    path('addUploadSurvey/', home.views.add_upload_survey, name = "add_upload_survey"),
    path('createQuestionsFile/', data_analysis.views.createQuestionsFile, name='createQuestionsFile'),
    path('uploadDataFile/', data_analysis.views.uploadDataFile, name='uploadDataFile'),
    path('createDataFile/', data_analysis.views.createDataFile, name='createDataFile'),
    path('uploadCoderFile/', prepare_reconciliation.views.uploadCoderFile, name='uploadCoderFile'),
    path('createCoderFile/', prepare_reconciliation.views.createCoderFile, name='createCoderFile'),
    path('reviewSurveyQuestions/', data_analysis.views.reviewSurveyQuestions, name='reviewSurveyQuestions'),
    path('updateSurveyQuestions/', data_analysis.views.updateSurveyQuestions, name='updateSurveyQuestions'),
    path('chooseCodes/', coding.views.chooseCodes, name='chooseCodes'),
    path('reloadCodes/', coding.views.reloadCodes, name='reloadCodes'),
    path('searchCodes/<str:question_id>/<str:term>/', coding.views.searchCodes, name='searchCodes'),
    path('applyReconciliation/', prepare_reconciliation.views.applyReconciliation, name='applyReconciliation'),
    path('run_reconciliation/', prepare_reconciliation.views.run_reconciliation, name='run_reconciliation'),
    path('showPlot/', plot.views.showPlot, name='showPlot'),
    path('showReport/', plot.views.showReport, name='showReport'),
    path('showComparison/', plot.views.showComparisonTable, name="showComparison"),
    path('browse/', data_browser.views.browse, name='browse'), 
    path('removeSurveyForm/', home.views.removeSurveyForm, name = "removeSurveyForm"),
    path('removeSurvey/', home.views.remove_survey, name = "remove_survey"),
    path('openCoding/', coding.open_coding.open_coding, name='open_coding'),
    path('selectCoder/', coding.views.selectCoder, name = "selectCoder"),
    path('addCoder/', coding.views.addCoder, name = "addCoder"),
    path('updateInvalid/', data_analysis.views.updateInvalids, name = "updateInvalid"),
    path('addInvalid/', data_analysis.views.addInvalid, name="addInvalid"),
    path('removeInvalid/', data_analysis.views.removeInvalid, name="removeInvalid")
]
