import json
import numpy as np
from nlp.embedder import compute_similarity, embed_user_profile
from jobs.models import JobListing
from accounts.models import UserProfile
from django.db.models import Q

def get_content_based_recommendations(user, top_n=20) -> list:
    """
    Computes content-based recommendations by comparing the user's profile 
    embedding against all available job embeddings using cosine similarity.
    
    Returns a sorted list of dictionaries containing the top_n jobs.
    """
    try:
        # 1. Fetch the UserProfile for the given user
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return []

    # 2. Generate the SBERT embedding vector for the user profile
    user_embedding = embed_user_profile(user_profile)
    
    if not user_embedding:
        return []

    # 3. Fetch all jobs that have successfully computed embeddings
    jobs = JobListing.objects.exclude(Q(embedding__isnull=True) | Q(embedding__exact=''))
    
    scored_jobs = []
    
    # 4. Compare the user against every job
    for job in jobs:
        try:
            # Load the job embedding from the JSON string
            job_embedding = json.loads(job.embedding)
            
            # Compute cosine similarity
            score = compute_similarity(user_embedding, job_embedding)
            
            # Store tuple
            scored_jobs.append({
                "job": job,
                "score": score,
                "method": "content_based"
            })
            
        except (json.JSONDecodeError, TypeError, ValueError):
            # If a specific job's embedding string is somehow corrupted, gracefully skip it
            continue
            
    # 5. Sort all jobs by their similarity score descending (highest matches first)
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # 6. Return exactly the top_n results requested
    return scored_jobs[:top_n]
