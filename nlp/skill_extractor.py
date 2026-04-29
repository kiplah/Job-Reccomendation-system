import spacy
import re
from bs4 import BeautifulSoup

# 1. Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Graceful fallback in case it needs to be downloaded in the environment
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# 2. Define a robust list of 40+ common tech skills (stored as a set for O(1) lookups)
SKILLS_KEYWORDS = {
    "python", "django", "javascript", "react", "sql", "postgresql", 
    "machine learning", "docker", "aws", "git", "rest api", "nlp", 
    "tensorflow", "scikit-learn", "flask", "node.js", "java", "c++", 
    "mongodb", "redis", "linux", "agile", "scrum", "kubernetes", 
    "azure", "gcp", "typescript", "angular", "vue.js", "html", 
    "css", "graphql", "apache kafka", "elasticsearch", "ci/cd", 
    "jenkins", "terraform", "ansible", "pytorch", "pandas", 
    "numpy", "tableau", "power bi", "data analysis", "ruby", 
    "ruby on rails", "php", "laravel", "go", "rust", "swift", 
    "kotlin", "android", "ios", "firebase"
}

def clean_text(text: str) -> str:
    """
    Removes HTML tags, extra whitespace, special characters, 
    and returns clean lowercase text ready for embedding.
    """
    if not text:
        return ""
    
    # Remove HTML tags safely using BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")
    
    # Remove special characters (keep alphanumeric, spaces, and tech symbols like C++, C#)
    text = re.sub(r'[^a-zA-Z0-9\s\.\#\+]', ' ', text)
    
    # Compress multiple whitespaces into a single space and strip borders
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Return lowercase text
    return text.lower()

def extract_skills(text: str) -> list:
    """
    Takes a job description string, uses spaCy to process it,
    matches against SKILLS_KEYWORDS, extracts ORG entities,
    and returns a deduplicated list of skills.
    """
    if not text:
        return []

    # Process the text with spaCy
    doc = nlp(text)
    
    extracted_skills = set()
    
    # Step A: Token matching (lemmatized and raw) against our explicit keyword list
    for token in doc:
        lemma_lower = token.lemma_.lower()
        text_lower = token.text.lower()
        
        if lemma_lower in SKILLS_KEYWORDS:
            extracted_skills.add(lemma_lower.title())
        if text_lower in SKILLS_KEYWORDS:
            extracted_skills.add(text_lower.title())
            
    # Step B: Noun chunks matching for multi-word skills (e.g., "machine learning", "rest api")
    for chunk in doc.noun_chunks:
        chunk_lower = chunk.text.lower().strip()
        if chunk_lower in SKILLS_KEYWORDS:
            extracted_skills.add(chunk_lower.title())
            
    # Step C: Extract ORG entities as potential tools or technologies
    for ent in doc.ents:
        if ent.label_ == "ORG":
            clean_org = ent.text.strip()
            # Filter out very long ORG names which are likely just company names, 
            # we only want short entities (e.g., "GitHub", "Vercel", "Datadog")
            if len(clean_org.split()) <= 2 and len(clean_org) > 1:
                # Add to set (capitalization preserved)
                extracted_skills.add(clean_org)
                
    # Return as a sorted list for consistent database storage
    return sorted(list(extracted_skills))
