from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=500, unique=True)
    date_posted = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"

class JobEmbedding(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='embedding')
    vector = models.JSONField(help_text="SBERT vector representation of the job description")
    
    def __str__(self):
        return f"Embedding for {self.job.title}"
