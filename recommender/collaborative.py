import numpy as np
from sklearn.decomposition import TruncatedSVD
from recommender.models import UserFeedback
from jobs.models import JobListing
from django.contrib.auth import get_user_model

def get_collaborative_recommendations(user, top_n=20) -> list:
    """
    Computes collaborative filtering recommendations using Matrix Factorization (TruncatedSVD).
    Analyzes historical ratings to find patterns and predict scores for unrated jobs.
    """
    User = get_user_model()
    
    # 1. Fetch all feedback records
    all_feedback = list(UserFeedback.objects.select_related('user', 'job').all())
    
    # 2. Cold Start Check: If fewer than 5 feedback records exist, we abort 
    # because matrix decomposition requires minimum density to be accurate.
    if len(all_feedback) < 5:
        return []

    # Get distinct users and jobs that are actually present in the feedback pool
    user_ids = list({fb.user_id for fb in all_feedback})
    job_ids = list({fb.job_id for fb in all_feedback})
    
    # If the requesting user isn't in the matrix (no interactions yet), we can't collaborate
    if user.id not in user_ids:
        return []

    # 3. Build lookup dictionaries to map IDs to matrix indices
    user_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
    job_to_idx = {jid: idx for idx, jid in enumerate(job_ids)}
    
    # Need a reverse lookup to fetch the actual Django model instance later
    # We pre-fetch the jobs to avoid doing N queries in the loop
    job_objects = {job.id: job for job in JobListing.objects.filter(id__in=job_ids)}
    idx_to_job = {idx: job_objects[jid] for jid, idx in job_to_idx.items()}

    # 4. Initialize the User-Item matrix with zeros
    matrix = np.zeros((len(user_ids), len(job_ids)))
    
    # Populate the matrix with explicit ratings (1-5)
    for fb in all_feedback:
        u_idx = user_to_idx[fb.user_id]
        j_idx = job_to_idx[fb.job_id]
        matrix[u_idx, j_idx] = fb.rating

    # 5. Apply TruncatedSVD to decompose the matrix
    # n_components cannot exceed the number of features minus 1
    n_components = min(10, len(user_ids) - 1, len(job_ids) - 1)
    
    # If the matrix is too small for even 1 component, fallback
    if n_components < 1:
        return []

    svd = TruncatedSVD(n_components=n_components, random_state=42)
    
    # Factorize
    matrix_reduced = svd.fit_transform(matrix)
    
    # Reconstruct the matrix to get the normalized predicted ratings!
    predicted_matrix = svd.inverse_transform(matrix_reduced)

    # 6. Extract the target user's row of predicted scores
    target_user_idx = user_to_idx[user.id]
    user_predictions = predicted_matrix[target_user_idx]

    # Find jobs the user has ALREADY rated to exclude them from the recommendations
    rated_job_ids = {fb.job_id for fb in all_feedback if fb.user_id == user.id}

    scored_jobs = []
    
    # Loop through the user's predicted row
    for j_idx, predicted_score in enumerate(user_predictions):
        job = idx_to_job[j_idx]
        
        # We only recommend unrated jobs
        if job.id not in rated_job_ids:
            scored_jobs.append({
                "job": job,
                "score": float(predicted_score),
                "method": "collaborative"
            })
            
    # 7. Sort the array descending by predicted score
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_jobs[:top_n]
