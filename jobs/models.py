from django.db import models

class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    skills_required = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    platform = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. LinkedIn, Indeed, Glassdoor")
    url = models.URLField(max_length=500, unique=True)
    date_posted = models.DateField(blank=True, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    embedding = models.TextField(blank=True, null=True, help_text="SBERT vector as JSON string")

    class Meta:
        ordering = ['-scraped_at']

    def __str__(self):
        return f"{self.title} at {self.company}"
