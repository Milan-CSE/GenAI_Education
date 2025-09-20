# engine/matcher.py
CAREERS = [
    {
        "role": "Data Scientist",
        "skills": ["python", "machine learning", "statistics", "sql"],
        "about": "Analyze data, build ML models, and derive insights."
    },
    {
        "role": "Backend Developer",
        "skills": ["python", "django", "sql", "api"],
        "about": "Build and maintain the server side of web apps."
    },
    {
        "role": "AI Engineer",
        "skills": ["python", "deep learning", "ml", "data pipelines"],
        "about": "Build AI-powered products using ML models."
    },
    {
        "role": "Cybersecurity Analyst",
        "skills": ["networking", "linux", "python", "security"],
        "about": "Protect systems and networks from cyber threats."
    },
]

def match_careers(user_skills: list[str]) -> list[dict]:
    matches = []
    user_skills_set = set([s.lower() for s in user_skills])
    for c in CAREERS:
        have = len([s for s in c["skills"] if s.lower() in user_skills_set])
        match_score = int((have / len(c["skills"])) * 100)
        missing = [s for s in c["skills"] if s.lower() not in user_skills_set]
        matches.append({
            "role": c["role"],
            "match": match_score,
            "about": c["about"],
            "missing": missing
        })
    return sorted(matches, key=lambda m: m["match"], reverse=True)
