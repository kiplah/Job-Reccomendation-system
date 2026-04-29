from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Seeds a test user into the database for testing the AI recommendations'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='victor', help='Username for the test user')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options.get('username')
        
        # 1. Create or fetch the user
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created new user '{username}'!"))
        else:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Updating their profile..."))
            
        # 2. Update the UserProfile (which was automatically created by the post_save signal)
        from accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Inject some rich metadata so the SBERT vector has robust text to analyze
        profile.skills = "Python, Django, PostgreSQL, Docker, REST API, Machine Learning"
        profile.education = "Bachelor of Computer Science"
        profile.experience_years = 4
        profile.career_preferences = "Looking for remote backend engineering roles focusing on Python APIs and architecture."
        profile.location = "Remote"
        profile.profile_complete = True
        
        profile.save()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully populated rich metadata into the UserProfile for '{username}'!"))
        self.stdout.write(self.style.WARNING(f"You can now run: python manage.py generate_recommendations --user {username}"))
