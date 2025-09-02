from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    examiner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_exams")
    code = models.CharField(max_length=12, unique=True, default="")
    num_questions = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=30)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.code})"


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.text[:50]} ({'correct' if self.is_correct else 'wrong'})"


class ExamSession(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="sessions")
    examinee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_sessions")
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    is_submitted = models.BooleanField(default=False)

    def is_active(self) -> bool:
        if self.is_submitted:
            return False
        if self.exam.duration_minutes:
            return timezone.now() < self.started_at + timezone.timedelta(minutes=self.exam.duration_minutes)
        return True


class Answer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session", "question")

# Create your models here.
