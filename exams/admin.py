from django.contrib import admin
from .models import Exam, Question, Choice, ExamSession, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "examiner", "num_questions", "duration_minutes", "is_published", "created_at")
    list_filter = ("is_published", "created_at", "examiner")
    search_fields = ("title", "code", "examiner__username")
    readonly_fields = ("code", "created_at")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "order", "text")
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ("exam", "examinee", "started_at", "completed_at", "is_submitted", "score")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "chosen_choice", "is_correct", "answered_at")

# Register your models here.
