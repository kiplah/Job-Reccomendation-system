from django.contrib import admin
from .models import Job, JobEmbedding

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'is_active', 'date_posted')
    search_fields = ('title', 'company', 'location')
    list_filter = ('is_active',)

admin.site.register(JobEmbedding)
