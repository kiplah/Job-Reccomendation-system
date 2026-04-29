from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'experience_years', 'profile_complete', 'created_at')
    search_fields = ('user__username', 'location', 'skills')
    list_filter = ('profile_complete',)
