from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('job/<int:id>/', views.job_detail_view, name='job_detail'),
    path('apply/<int:id>/', views.mark_applied_view, name='mark_applied'),
    path('feedback/', views.feedback_view, name='feedback'),
]
