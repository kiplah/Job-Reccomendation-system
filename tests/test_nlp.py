import pytest
from nlp.skill_extractor import clean_text, extract_skills
from nlp.embedder import generate_embedding, compute_similarity

def test_clean_text_removes_html():
    """1. Verify clean_text() removes HTML tags from a sample string"""
    raw_text = "<p>We are looking for a <strong>Senior Developer</strong>!</p>"
    cleaned = clean_text(raw_text)
    
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert cleaned == "we are looking for a senior developer "

def test_extract_skills():
    """2. Verify extract_skills returns expected tech stack components"""
    text = "We need Python, Django and AWS experience"
    skills = extract_skills(text)
    
    # We lowercase the output for the assertion to ensure robustness against 
    # title-casing or dynamic ORG entity capitalization in the extractor
    skills_lower = [s.lower() for s in skills]
    
    assert "python" in skills_lower
    assert "django" in skills_lower
    assert "aws" in skills_lower

def test_generate_embedding_dimensions():
    """3. Verify generate_embedding returns a 384-length float list"""
    text = "software engineer with Python skills"
    embedding = generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert isinstance(embedding[0], float)

def test_compute_similarity_bounds():
    """4. Verify similarity score is bounded between 0 and 1"""
    embed_a = generate_embedding("python developer")
    embed_b = generate_embedding("java backend engineer")
    
    score = compute_similarity(embed_a, embed_b)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

def test_compute_similarity_identical_texts():
    """5. Verify identical texts produce a near-perfect similarity score"""
    text = "expert machine learning engineer with 5 years experience"
    embed_a = generate_embedding(text)
    embed_b = generate_embedding(text)
    
    score = compute_similarity(embed_a, embed_b)
    
    # Floating point precision mathematically prevents a perfect 1.00000 
    # natively with cos_sim, so we test > 0.99
    assert score > 0.99
