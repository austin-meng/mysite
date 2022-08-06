from django.contrib import admin
from .models import Question
from . import models


class QuestionAdmin(admin.ModelAdmin):
    fields = ['pub_date', 'question_text']

admin.site.register(Question, QuestionAdmin)
# admin.site.register(models.User)