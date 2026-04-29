import json
from django.core.management.base import BaseCommand
from django.db.models import Q
from jobs.models import JobListing
from nlp.skill_extractor import clean_text
from nlp.embedder import generate_embedding

class Command(BaseCommand):
    help = 'Generates SBERT embeddings for all unprocessed job listings and saves them to the database.'

    def handle(self, *args, **options):
        # 1. Fetch all JobListing objects where embedding is null or empty string
        jobs = JobListing.objects.filter(Q(embedding__isnull=True) | Q(embedding__exact=''))
        
        total_jobs = jobs.count()
        if total_jobs == 0:
            self.stdout.write(self.style.SUCCESS("All jobs in the database already have embeddings!"))
            return
            
        self.stdout.write(self.style.WARNING(f"Starting SBERT embedding generation for {total_jobs} jobs..."))
        
        processed_count = 0
        
        # 2. Process each job
        for job in jobs:
            # We combine the title, skills, and description into one dense string.
            # This ensures the embedding captures the full context of the job posting!
            combined_text = f"{job.title} {job.skills_required} {job.description}"
            
            # Clean the text (removes HTML, special chars, etc.)
            cleaned_text = clean_text(combined_text)
            
            # Generate the vector list
            embedding_list = generate_embedding(cleaned_text)
            
            # Serialize the python list into a JSON string and save
            job.embedding = json.dumps(embedding_list)
            
            # Only update the embedding field for optimization
            job.save(update_fields=['embedding'])
            
            processed_count += 1
            
            # Print progress every 10 jobs
            if processed_count % 10 == 0:
                self.stdout.write(f"--> Embedded {processed_count}/{total_jobs} jobs...")
                
        # 3. Print total summary
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully generated and saved embeddings for {processed_count} jobs!"))
