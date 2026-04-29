from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add any extra auth-related fields here in the future
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    resume_text = models.TextField(blank=True, null=True, help_text="Parsed text from the user's resume")
    skills = models.JSONField(default=list, blank=True, help_text="List of extracted skills")
    experience_level = models.CharField(max_length=50, blank=True, null=True)
    profile_embedding = models.JSONField(blank=True, null=True, help_text="SBERT vector representation of the user's profile")

    def __str__(self):
        return f"{self.user.username}'s Profile"
