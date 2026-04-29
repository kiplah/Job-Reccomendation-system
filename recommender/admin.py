from django.contrib import admin
from .models import Recommendation, UserFeedback

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'score', 'seen', 'applied', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('seen', 'applied')
    ordering = ('-score',)

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'rating', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('rating',)
