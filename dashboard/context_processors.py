from recommender.models import Recommendation

def notifications(request):
    """
    Context processor to inject unread AI job recommendations into all templates
    for the notification bell dropdown.
    """
    if request.user.is_authenticated:
        # Fetch up to 5 unread recommendations
        unread_recs = Recommendation.objects.filter(user=request.user, seen=False).select_related('job').order_by('-created_at')[:5]
        unread_count = Recommendation.objects.filter(user=request.user, seen=False).count()
        return {
            'unread_notifications': unread_recs,
            'unread_count': unread_count
        }
    return {}
