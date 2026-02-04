import PyPDF2
import re
from typing import List, Dict

# Comprehensive tech skills dictionary
TECH_SKILLS = {
    'languages': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 
        'rust', 'kotlin', 'swift', 'php', 'ruby', 'scala', 'r'
    ],
    'frameworks': [
        'react', 'angular', 'vue', 'django', 'flask', 'spring boot', 
        'node.js', 'express', 'fastapi', 'next.js', 'react native', 
        'flutter', 'tensorflow', 'pytorch', 'scikit-learn'
    ],
    'databases': [
        'postgresql', 'mongodb', 'mysql', 'redis', 'cassandra', 
        'elasticsearch', 'dynamodb', 'oracle', 'sql server'
    ],
    'cloud': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'jenkins', 'ci/cd', 'github actions'
    ],
    'tools': [
        'git', 'jira', 'confluence', 'postman', 'swagger', 
        'linux', 'bash', 'graphql', 'rest api', 'microservices'
    ]
}

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_skills(text: str) -> List[str]:
    """Extract skills from text using pattern matching"""
    text_lower = text.lower()
    found_skills = []
    
    # Flatten all skills into one list
    all_skills = []
    for category, skills in TECH_SKILLS.items():
        all_skills.extend(skills)
    
    # Find skills in text
    for skill in all_skills:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return sorted(list(set(found_skills)))

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills by type"""
    categorized = {category: [] for category in TECH_SKILLS.keys()}
    
    for skill in skills:
        for category, category_skills in TECH_SKILLS.items():
            if skill in category_skills:
                categorized[category].append(skill)
    
    return {k: v for k, v in categorized.items() if v}  # Remove empty categories

def calculate_match_score(resume_skills: List[str], job_skills: List[str]) -> Dict:
    """Calculate compatibility percentage between resume and job"""
    if not job_skills:
        return {
            'score': 0,
            'matched_skills': [],
            'missing_skills': [],
            'extra_skills': resume_skills
        }
    
    matched = set(resume_skills) & set(job_skills)
    missing = set(job_skills) - set(resume_skills)
    extra = set(resume_skills) - set(job_skills)
    
    score = (len(matched) / len(job_skills)) * 100
    
    return {
        'score': round(score, 2),
        'matched_skills': sorted(list(matched)),
        'missing_skills': sorted(list(missing)),
        'extra_skills': sorted(list(extra))
    }