"""
logic.py - Core analysis logic: skill detection, ATS scoring, JD matching
"""

import re
from typing import Dict, List, Tuple
from skills import SKILLS_DB, HIGH_VALUE_KEYWORDS, SECTION_KEYWORDS


def detect_skills(text: str) -> Dict[str, List[str]]:
    """
    Detect skills from resume text, categorized by type.
    Returns dict of category -> list of detected skills.
    """
    if not text:
        return {cat: [] for cat in SKILLS_DB}

    text_lower = text.lower()
    detected = {}

    for category, skills in SKILLS_DB.items():
        found = []
        for skill in skills:
            # Use word boundary matching for short skills, substring for longer ones
            if len(skill) <= 3:
                pattern = r'\b' + re.escape(skill) + r'\b'
            else:
                pattern = re.escape(skill)
            if re.search(pattern, text_lower):
                found.append(skill)
        detected[category] = found

    return detected


def detect_sections(text: str) -> Dict[str, bool]:
    """
    Detect common resume sections (experience, education, etc.)
    Returns dict of section_name -> bool (present or not).
    """
    if not text:
        return {sec: False for sec in SECTION_KEYWORDS}

    text_lower = text.lower()
    sections_found = {}

    for section, keywords in SECTION_KEYWORDS.items():
        found = any(kw in text_lower for kw in keywords)
        sections_found[section] = found

    return sections_found


def calculate_ats_score(
    text: str,
    detected_skills: Dict[str, List[str]],
    sections: Dict[str, bool]
) -> Tuple[int, Dict[str, float]]:
    """
    Calculate ATS (Applicant Tracking System) score from 0-100.
    Returns (total_score, breakdown_dict).

    Scoring breakdown:
    - Skill coverage:     40 points
    - Keyword density:    25 points
    - Section presence:   20 points
    - Word count/length:  15 points
    """
    if not text:
        return 0, {}

    text_lower = text.lower()
    breakdown = {}

    # 1. Skill coverage score (40 pts)
    total_skills_in_db = sum(len(v) for k, v in SKILLS_DB.items() if k != "Soft Skills")
    total_detected = sum(len(v) for k, v in detected_skills.items() if k != "Soft Skills")
    # Cap at 80 unique skills as "full coverage" benchmark
    coverage_ratio = min(total_detected / 80, 1.0)
    skill_score = round(coverage_ratio * 40, 1)
    breakdown["Skill Coverage"] = skill_score

    # 2. High-value keyword density (25 pts)
    keyword_hits = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw in text_lower)
    density_ratio = min(keyword_hits / len(HIGH_VALUE_KEYWORDS), 1.0)
    keyword_score = round(density_ratio * 25, 1)
    breakdown["Keyword Density"] = keyword_score

    # 3. Section presence (20 pts)
    critical_sections = ["experience", "education", "skills", "projects"]
    section_hits = sum(1 for s in critical_sections if sections.get(s, False))
    section_score = round((section_hits / len(critical_sections)) * 20, 1)
    breakdown["Section Structure"] = section_score

    # 4. Resume length/content depth (15 pts)
    word_count = len(text.split())
    if word_count >= 400:
        length_score = 15.0
    elif word_count >= 200:
        length_score = round((word_count / 400) * 15, 1)
    else:
        length_score = round((word_count / 200) * 8, 1)
    breakdown["Content Depth"] = length_score

    total = min(int(skill_score + keyword_score + section_score + length_score), 100)
    return total, breakdown


def get_missing_skills(detected_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Identify skills present in the database but missing from the resume.
    Returns dict of category -> list of missing skills (top 10 per category).
    """
    missing = {}
    for category, all_skills in SKILLS_DB.items():
        detected_set = set(detected_skills.get(category, []))
        missing_in_cat = [s for s in all_skills if s not in detected_set]
        # Limit to top 10 missing per category for readability
        missing[category] = missing_in_cat[:10]
    return missing


def match_job_description(resume_text: str, job_desc: str) -> Tuple[float, List[str], List[str]]:
    """
    Compute match score between resume and a job description.
    Returns (match_percentage, matched_keywords, missing_keywords).
    """
    if not resume_text or not job_desc:
        return 0.0, [], []

    resume_lower = resume_text.lower()
    jd_lower = job_desc.lower()

    # Extract meaningful words from JD (3+ chars, not stopwords)
    stopwords = {
        "the", "and", "for", "with", "you", "are", "this", "that", "have",
        "will", "your", "our", "from", "can", "has", "was", "been", "not",
        "but", "they", "their", "its", "into", "all", "any", "some", "who",
        "what", "when", "where", "how", "which", "also", "more", "than",
        "about", "should", "must", "would", "could", "other", "these",
        "those", "such", "both", "each", "most", "over", "very", "well"
    }

    # Get all words from JD
    jd_words = re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', jd_lower)
    jd_keywords = list(set(w for w in jd_words if w not in stopwords))

    if not jd_keywords:
        return 0.0, [], []

    matched = [kw for kw in jd_keywords if kw in resume_lower]
    missing = [kw for kw in jd_keywords if kw not in resume_lower]

    # Sort missing by likely importance (longer words tend to be more specific)
    missing_sorted = sorted(missing, key=len, reverse=True)[:20]
    matched_sorted = sorted(matched, key=len, reverse=True)[:20]

    score = round((len(matched) / len(jd_keywords)) * 100, 1)
    return min(score, 100.0), matched_sorted, missing_sorted


def get_ats_color(score: int) -> str:
    """Return color indicator based on ATS score."""
    if score >= 70:
        return "green"
    elif score >= 40:
        return "orange"
    else:
        return "red"


def get_ats_label(score: int) -> str:
    """Return label for ATS score."""
    if score >= 70:
        return "Strong"
    elif score >= 40:
        return "Moderate"
    else:
        return "Needs Work"
