from django.db import models
from django.conf import settings
from jobs.models import JobListing

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField(help_text="Cosine similarity score")
    seen = models.BooleanField(default=False)
    applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.job.title} (Score: {self.score:.2f})"


class UserFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.user.username} for {self.job.title}: {self.rating} stars"
