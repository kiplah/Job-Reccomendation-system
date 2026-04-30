import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from recommender.models import Recommendation, UserFeedback
from jobs.models import JobListing

@login_required
def dashboard_view(request):
    """
    Fetches the top 10 AI recommendations for the active user and passes them to the template.
    """
    recommendations = Recommendation.objects.filter(user=request.user).select_related('job').order_by('-score')[:10]
    
    context = {
        'recommendations': recommendations,
        'has_recommendations': len(recommendations) > 0
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def job_detail_view(request, id):
    """
    Shows details of a specific job and secretly marks the Recommendation as 'seen'
    so we can track user engagement metrics.
    """
    job = get_object_or_404(JobListing, id=id)
    
    # Check if a recommendation exists for this specific job and user
    rec = Recommendation.objects.filter(user=request.user, job=job).first()
    if rec and not rec.seen:
        rec.seen = True
        rec.save(update_fields=['seen'])
        
    return render(request, 'dashboard/job_detail.html', {'job': job})

@login_required
@require_POST
def mark_applied_view(request, id):
    """
    API Endpoint: Marks a job as 'applied' when the user clicks the apply button.
    """
    job = get_object_or_404(JobListing, id=id)
    rec = Recommendation.objects.filter(user=request.user, job=job).first()
    
    if rec:
        rec.applied = True
        rec.save(update_fields=['applied'])
        
    return JsonResponse({"status": "ok"})

@login_required
@require_POST
def feedback_view(request):
    """
    API Endpoint: Accepts a 1-5 rating from the user and saves it to UserFeedback.
    This dynamically feeds our Matrix Factorization Collaborative engine!
    """
    try:
        # Handle both raw JSON fetches or standard POST form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            job_id = data.get('job_id')
            rating = data.get('rating')
        else:
            job_id = request.POST.get('job_id')
            rating = request.POST.get('rating')
            
        if not job_id or not rating:
            return JsonResponse({"error": "Missing job_id or rating"}, status=400)
            
        job = get_object_or_404(JobListing, id=job_id)
        rating = int(rating)
        
        # Security bound
        if rating < 1 or rating > 5:
            return JsonResponse({"error": "Rating must be between 1 and 5"}, status=400)
            
        # Update or create the feedback mathematically
        feedback, created = UserFeedback.objects.update_or_create(
            user=request.user,
            job=job,
            defaults={'rating': rating}
        )
        
        return JsonResponse({"status": "ok"})
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid payload format"}, status=400)
