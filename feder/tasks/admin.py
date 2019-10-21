from django.contrib import admin

from feder.tasks.models import Answer, Survey


class AnswerInline(admin.TabularInline):
    """
        Tabular Inline View for Answer
    """

    model = Answer
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """
        Admin View for Survey
    """

    list_display = ("task", "user", "light_user", "created", "modified")
    inlines = [AnswerInline]
