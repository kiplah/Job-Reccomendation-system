import pytest
import json
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from jobs.models import JobListing
from recommender.models import UserFeedback, Recommendation
from recommender.content_based import get_content_based_recommendations
from recommender.collaborative import get_collaborative_recommendations
from recommender.hybrid import generate_recommendations

User = get_user_model()

@pytest.fixture
def setup_data(db):
    """
    Creates simple model fixtures for testing.
    We inject exactly 2 users and 3 jobs into the database.
    """
    # 1. Create Users
    user1 = User.objects.create_user(username="testuser1", password="password")
    user2 = User.objects.create_user(username="testuser2", password="password")
    
    # UserProfile is created automatically via our post_save signal
    profile1 = user1.userprofile
    profile1.skills = "Python, Django, AWS"
    profile1.save()
    
    # 2. Create Jobs with valid embeddings (384 dimensions for SBERT)
    # We use small variances so the cosine math doesn't crash on identical vectors
    job1 = JobListing.objects.create(
        title="Python Backend Developer",
        company="TechCorp",
        url="http://job1.com",
        embedding=json.dumps([0.1] * 384)
    )
    
    job2 = JobListing.objects.create(
        title="Django Engineer",
        company="WebCorp",
        url="http://job2.com",
        embedding=json.dumps([0.2] * 384)
    )
    
    job3 = JobListing.objects.create(
        title="Frontend Dev",
        company="UIInc",
        url="http://job3.com",
        embedding=json.dumps([0.05] * 384)
    )
    
    return {
        "user1": user1,
        "user2": user2,
        "jobs": [job1, job2, job3]
    }

@pytest.mark.django_db
def test_content_based_returns_list(setup_data):
    """1. Verify get_content_based_recommendations() returns a list"""
    user = setup_data["user1"]
    results = get_content_based_recommendations(user, top_n=5)
    
    assert isinstance(results, list)

@pytest.mark.django_db
def test_content_based_keys_and_bounds(setup_data):
    """2 & 3. Verify required keys and score boundaries between 0.0 and 1.0"""
    user = setup_data["user1"]
    results = get_content_based_recommendations(user, top_n=5)
    
    # Ensure there are actually results returned to validate
    assert len(results) > 0
    
    for item in results:
        # Check required dictionary keys
        assert "job" in item
        assert "score" in item
        assert "method" in item
        
        # Check float math bounds
        assert 0.0 <= item["score"] <= 1.0

@pytest.mark.django_db
def test_content_based_sorted_descending(setup_data):
    """4. Verify results are strictly sorted by score descending"""
    user = setup_data["user1"]
    results = get_content_based_recommendations(user, top_n=5)
    
    scores = [item["score"] for item in results]
    
    # Sorting a list descending should identically match the current order
    assert scores == sorted(scores, reverse=True)

@pytest.mark.django_db
def test_collaborative_cold_start(setup_data):
    """5. Verify empty list is returned when feedback records < 5 (cold start)"""
    user = setup_data["user1"]
    
    # We deliberately create exactly 3 feedback records
    UserFeedback.objects.create(user=user, job=setup_data["jobs"][0], rating=5)
    UserFeedback.objects.create(user=user, job=setup_data["jobs"][1], rating=4)
    UserFeedback.objects.create(user=setup_data["user2"], job=setup_data["jobs"][2], rating=3)
    
    assert UserFeedback.objects.count() == 3
    
    # Ensure algorithm aborts gracefully
    results = get_collaborative_recommendations(user, top_n=5)
    assert results == []

@pytest.mark.django_db
def test_generate_recommendations_creates_db_objects(setup_data):
    """6. Verify generate_recommendations() caches Recommendation objects in the database"""
    user = setup_data["user1"]
    
    # Pre-condition: No recommendations exist
    assert Recommendation.objects.filter(user=user).count() == 0
    
    # Trigger the hybrid engine
    results = generate_recommendations(user, top_n=2)
    
    # Check that it returns actual Django model objects
    assert len(results) > 0
    assert isinstance(results[0], Recommendation)
    
    # Verify persistence: They must exist physically in the test database
    db_count = Recommendation.objects.filter(user=user).count()
    assert db_count > 0
    assert db_count <= 2
