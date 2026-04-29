import numpy as np
from sentence_transformers import SentenceTransformer, util

# 1 & 2. Load the lightweight model globally to cache it at the module level
# This ensures it is loaded into memory only once when the Django process starts.
# "all-MiniLM-L6-v2" generates 384-dimensional vectors and is highly optimized.
print("Initializing SBERT Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str) -> list:
    """
    Takes a text string, generates a dense vector embedding, 
    and returns it as a JSON-serializable Python list.
    """
    if not text or not str(text).strip():
        return []
        
    # encode() returns a numpy array, we convert to a standard list for JSON storage in the DB
    embedding = model.encode(text)
    return embedding.tolist()

def compute_similarity(embedding1: list, embedding2: list) -> float:
    """
    Computes cosine similarity between two embedding lists.
    Returns a float score between 0.0 and 1.0 representing the match percentage.
    """
    if not embedding1 or not embedding2:
        return 0.0
        
    # util.cos_sim computes cosine similarity and returns a 2D tensor.
    # We extract the pure float value.
    tensor_result = util.cos_sim(embedding1, embedding2)
    score = float(tensor_result[0][0].item())
    
    # Ensure the score strictly bounds between 0 and 1
    return max(0.0, min(1.0, score))

def embed_user_profile(user_profile) -> list:
    """
    Takes a Django UserProfile instance, compiles a single comprehensive 
    text string of their professional identity, and generates an embedding.
    """
    parts = []
    
    # Extract model fields dynamically
    if getattr(user_profile, 'skills', None):
        parts.append(f"Skills: {user_profile.skills}")
        
    if getattr(user_profile, 'education', None):
        parts.append(f"Education: {user_profile.education}")
        
    if getattr(user_profile, 'experience_years', None):
        parts.append(f"Experience: {user_profile.experience_years} years")
        
    if getattr(user_profile, 'career_preferences', None):
        parts.append(f"Preferences: {user_profile.career_preferences}")
        
    # Combine into a single dense text block describing the user
    combined_text = " | ".join(parts)
    
    # Generate and return the embedding list
    return generate_embedding(combined_text)
