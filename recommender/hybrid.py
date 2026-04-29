from recommender.content_based import get_content_based_recommendations
from recommender.collaborative import get_collaborative_recommendations
from recommender.models import Recommendation

def generate_recommendations(user, top_n=10):
    """
    Generates a hybrid set of recommendations combining NLP embeddings and 
    collaborative matrix factorization. Saves the top matches to the database.
    """
    # 1. Fetch top 30 candidates from both algorithms
    content_recs = get_content_based_recommendations(user, top_n=30)
    collab_recs = get_collaborative_recommendations(user, top_n=30)
    
    # 2. Use a dictionary to merge scores, keyed by the job ID
    job_scores = {}
    
    # Populate the dictionary with content-based scores
    for rec in content_recs:
        job = rec["job"]
        job_scores[job.id] = {
            "job": job,
            "content_score": rec["score"],
            "collab_score": 0.0,
        }
        
    # Merge in the collaborative scores
    for rec in collab_recs:
        job = rec["job"]
        if job.id in job_scores:
            job_scores[job.id]["collab_score"] = rec["score"]
        else:
            job_scores[job.id] = {
                "job": job,
                "content_score": 0.0,
                "collab_score": rec["score"],
            }
            
    # 3. Calculate final hybrid scores based on the specified weights
    for j_id, data in job_scores.items():
        c_score = data["content_score"]
        collab_score = data["collab_score"]
        
        # Scenario A: Job appears in both algorithms (highest confidence)
        if c_score > 0 and collab_score > 0:
            data["final_score"] = (0.7 * c_score) + (0.3 * collab_score)
            
        # Scenario B: Job only appears in Content-Based filtering
        elif c_score > 0:
            data["final_score"] = c_score
            
        # Scenario C: Job only appears in Collaborative filtering
        else:
            data["final_score"] = 0.5 * collab_score
            
    # 4. Convert dict to list and sort strictly by final_score descending
    merged_list = list(job_scores.values())
    merged_list.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 5. Extract only the top_n results
    top_jobs = merged_list[:top_n]
    saved_recommendations = []
    
    # 6. Save or update the final results in the database
    for data in top_jobs:
        rec, created = Recommendation.objects.update_or_create(
            user=user,
            job=data["job"],
            defaults={"score": data["final_score"]}
        )
        saved_recommendations.append(rec)
        
    return saved_recommendations

def get_user_recommendations(user, top_n=10):
    """
    Fetches the highest scoring saved recommendations for a given user directly 
    from the database, minimizing processing time for page loads.
    Returns a QuerySet optimized with select_related.
    """
    return Recommendation.objects.filter(user=user).select_related('job').order_by('-score')[:top_n]
