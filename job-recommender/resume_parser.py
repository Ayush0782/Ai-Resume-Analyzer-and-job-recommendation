# ============================================================
# resume_parser.py — PDF Parsing and Skill Extraction
# Uses pdfplumber to read PDF text
# Uses a predefined skill list to extract relevant skills
# ============================================================

import pdfplumber
import re

# -------------------------------------------------------
# Master list of skills to look for in a resume
# You can expand this list as needed
# -------------------------------------------------------
SKILL_KEYWORDS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
    "php", "swift", "kotlin", "go", "rust", "scala", "r", "matlab",

    # Web Development
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "fastapi", "bootstrap", "tailwind", "next.js",
    "rest api", "graphql", "jquery",

    # Data Science / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "data analysis", "data science", "computer vision",
    "neural network", "transformers", "hugging face",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "firebase", "elasticsearch", "cassandra",

    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "ci/cd", "jenkins", "terraform", "linux", "git", "github",
    "devops", "microservices",

    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "etl", "data pipeline",
    "power bi", "tableau", "excel",

    # Cybersecurity
    "cybersecurity", "penetration testing", "ethical hacking",
    "network security", "firewalls", "siem", "vulnerability assessment",

    # Soft Skills / Business
    "project management", "agile", "scrum", "jira", "communication",
    "leadership", "teamwork", "problem solving",

    # Mobile
    "android", "ios", "flutter", "react native", "xamarin",

    # Design
    "figma", "photoshop", "illustrator", "ui/ux", "wireframing",
]


def extract_text_from_pdf(filepath):
    """
    Extract raw text from a PDF file using pdfplumber.
    Returns all text as a single lowercase string.
    """
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()


def extract_skills(text):
    """
    Scan resume text for known skills.
    Returns a sorted list of matched skills.
    """
    found_skills = []
    for skill in SKILL_KEYWORDS:
        # Use word boundary matching for accuracy
        # e.g., "r" should not match inside "react"
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill.title())  # Capitalize nicely

    return sorted(set(found_skills))  # Remove duplicates


def extract_keywords(text):
    """
    Extract general important keywords from resume text.
    Filters out common stop words and very short words.
    """
    # Common English stop words to filter out
    stop_words = {
        "the", "and", "or", "in", "on", "at", "to", "for", "of", "a",
        "an", "is", "are", "was", "were", "with", "this", "that", "it",
        "be", "as", "by", "from", "have", "has", "had", "not", "but",
        "we", "i", "my", "your", "our", "their", "he", "she", "they",
        "you", "me", "him", "her", "us", "also", "can", "will", "do",
        "did", "does", "so", "if", "up", "out", "all", "more", "than",
        "new", "such", "about", "which", "when", "where", "who", "how",
        "been", "its", "into", "through", "during", "including", "while",
    }

    # Tokenize: split by spaces and punctuation
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)

    # Filter stop words and short tokens
    keywords = [
        word for word in words
        if word.lower() not in stop_words
    ]

    # Count frequency
    from collections import Counter
    freq = Counter(keywords)

    # Return top 20 most frequent keywords
    top_keywords = [word.title() for word, _ in freq.most_common(20)]
    return top_keywords


def extract_resume_data(filepath):
    """
    Main function: combines text extraction, skill detection,
    and keyword extraction.
    Returns a dict with full_text, skills, and keywords.
    """
    full_text = extract_text_from_pdf(filepath)

    skills = extract_skills(full_text)
    keywords = extract_keywords(full_text)

    return {
        "full_text": full_text,
        "skills": skills,
        "keywords": keywords
    }
