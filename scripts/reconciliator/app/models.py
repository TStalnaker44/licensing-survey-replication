from django.db import models


class Questions(models.Model):
    id = models.IntegerField(primary_key=True)
    qid = models.TextField()
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'questions'


class Coders(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.TextField()

    class Meta:
        managed = False
        db_table = 'coders'


class ResponseCodes(models.Model):
    id = models.IntegerField(primary_key=True)
    qid = models.TextField()
    pid = models.IntegerField()
    coder_combo = models.TextField()
    codes = models.TextField()

    class Meta:
        managed = False
        db_table = 'response_codes'


class Responses(models.Model):
    id = models.IntegerField(primary_key=True)
    pid = models.IntegerField()
    qid = models.TextField()
    response = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'responses'


class Terms(models.Model):
    # id = models.AutoField(unique=True)
    id = models.IntegerField(primary_key=True)
    term = models.TextField()
    definition = models.TextField()
    qid = models.TextField()

    class Meta:
        managed = False
        db_table = 'terms'


# Models for opencode database
class Survey(models.Model):
    internal_id = models.TextField(null=False, unique=True)

    class Database:
        db = "opencode"


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(null=False)

    class Database:
        db = "opencode"


class Respondent(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='respondents')
    qualtrics_id = models.TextField(unique=True)

    class Database:
        db = "opencode"


class Response(models.Model):
    json_id = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE, related_name='respondents')
    response = models.TextField(null=False)

    class Database:
        db = "opencode"
