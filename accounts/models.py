from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EXAMINER = "EXAMINER", "Examiner"
        EXAMINEE = "EXAMINEE", "Examinee"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EXAMINEE)

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_examiner(self):
        return self.role == self.Role.EXAMINER

    def is_examinee(self):
        return self.role == self.Role.EXAMINEE
