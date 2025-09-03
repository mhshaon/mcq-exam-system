from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EXAMINER = "EXAMINER", "Examiner"
        EXAMINEE = "EXAMINEE", "Examinee"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EXAMINEE)
    
    # Ensure email field is properly configured
    email = models.EmailField(unique=True, blank=False, null=False)
    
    # Make username case-insensitive for better user experience
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_examiner(self):
        return self.role == self.Role.EXAMINER

    def is_examinee(self):
        return self.role == self.Role.EXAMINEE
