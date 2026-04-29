from django.contrib import admin
from .models import JobListing

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'platform', 'is_active', 'scraped_at')
    search_fields = ('title', 'company', 'location', 'platform')
    list_filter = ('is_active', 'platform', 'scraped_at')
