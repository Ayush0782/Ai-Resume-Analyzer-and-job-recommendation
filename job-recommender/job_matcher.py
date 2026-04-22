
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests


JOBS_FILE = os.path.join(os.path.dirname(__file__), "data", "jobs.json")


def load_jobs():
    #with open(JOBS_FILE, "r") as f:
        #jobs = json.load(f)
    #return jobs
    """Fetch real-time jobs from Remotive API"""

    url = "https://remotive.com/api/remote-jobs"

    response = requests.get(url)
    data = response.json()

    jobs = []

    for item in data.get("jobs", [])[:50]:  # limit for speed
        jobs.append({
            "title": item["title"],
            "company": item["company_name"],
            "category": item["category"],
            "description": item["description"],
            "required_skills": item.get("tags", [])
        })

    return jobs


def get_job_recommendations(resume_text, top_n=5):
    """
    Compare resume text against all job descriptions
    using TF-IDF vectorization + cosine similarity.

    Parameters:
        resume_text (str): Full extracted resume text
        top_n (int): Number of top jobs to return

    Returns:
        List of dicts: top_n job recommendations with scores
    """
    jobs = load_jobs()

    
    job_descriptions = [job["description"] for job in jobs]

 
    all_documents = [resume_text] + job_descriptions

    
    vectorizer = TfidfVectorizer(
        stop_words="english",   # Remove common English words
        ngram_range=(1, 2),     # Use single words AND two-word phrases
        max_features=5000       # Limit vocabulary size for speed
    )
    tfidf_matrix = vectorizer.fit_transform(all_documents)

    # Calculate cosine similarity between resume and each job
    # Index 0 = resume, 1..N = job descriptions
    resume_vector = tfidf_matrix[0]
    job_vectors = tfidf_matrix[1:]

    similarity_scores = cosine_similarity(resume_vector, job_vectors)[0]

    # Rank jobs by similarity score (highest first)
    ranked_indices = similarity_scores.argsort()[::-1]

    # Build result list for top_n jobs
    recommendations = []
    for i in ranked_indices[:top_n]:
        job = jobs[i]
        score = float(similarity_scores[i])

        # Find which required skills match the resume
        resume_lower = resume_text.lower()
        matched_skills = [
            skill for skill in job.get("required_skills", [])
            if skill.lower() in resume_lower
        ]

        recommendations.append({
            "title": job["title"],
            "company": job.get("company", "Various Companies"),
            "category": job.get("category", "Technology"),
            "description": job["description"][:200] + "...",  # Short preview
            "required_skills": job.get("required_skills", []),
            "matched_skills": matched_skills,
            "match_score": round(score * 100, 1)  # Convert to percentage
        })

    return recommendations
