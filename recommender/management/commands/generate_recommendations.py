from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommender.hybrid import generate_recommendations
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Batch generates hybrid AI recommendations for users and saves them to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user', 
            type=str, 
            help='Username or User ID to generate recommendations for a specific user'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        user_query = options.get('user')
        
        users_to_process = []
        
        # 1 & 2. Parse the optional user argument
        if user_query:
            if user_query.isdigit():
                user = User.objects.filter(id=int(user_query)).first()
            else:
                user = User.objects.filter(username=user_query).first()
                
            if not user:
                self.stdout.write(self.style.ERROR(f"User '{user_query}' not found in the database!"))
                return
            users_to_process.append(user)
            
        # 3. If no user given, batch process all users with complete profiles
        else:
            profiles = UserProfile.objects.filter(profile_complete=True).select_related('user')
            users_to_process = [p.user for p in profiles]
            
            if not users_to_process:
                self.stdout.write(self.style.WARNING("No users found with complete profiles (profile_complete=True)."))
                return

        self.stdout.write(self.style.WARNING(f"\nStarting Hybrid Recommendation Engine for {len(users_to_process)} user(s)..."))
        
        for user in users_to_process:
            self.stdout.write(f"\nAnalyzing data for user: @{user.username}")
            
            # 4. Generate recommendations (this automatically runs both Content & Collaborative algorithms and saves them)
            recs = generate_recommendations(user, top_n=10)
            
            if not recs:
                self.stdout.write(self.style.ERROR(f"  [!] Failed to generate recommendations for {user.username}."))
                continue
                
            self.stdout.write(self.style.SUCCESS(f"  [+] Saved {len(recs)} highly curated recommendations to the database!"))
            self.stdout.write("  Top 3 Matches:")
            
            # 5. Print out the top 3 scores and jobs
            for i, rec in enumerate(recs[:3]):
                # Formatting the score to two decimal places for aesthetics
                self.stdout.write(f"    {i+1}. [{rec.score:.2f}] {rec.job.title} @ {rec.job.company}")
                
        self.stdout.write(self.style.SUCCESS("\nRecommendation batch cycle fully completed!"))
