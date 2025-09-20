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
        "role": "Frontend Developer",
        "skills": ["javascript", "react", "css", "html"],
        "about": "Design and implement user interfaces for web apps."
    },
    {
        "role": "Full Stack Developer",
        "skills": ["javascript", "react", "node.js", "sql", "api"],
        "about": "Work on both frontend and backend of applications."
    },
    {
        "role": "AI Engineer",
        "skills": ["python", "deep learning", "ml", "data pipelines"],
        "about": "Build AI-powered products using ML models."
    },
    {
        "role": "Machine Learning Engineer",
        "skills": ["python", "tensorflow", "pytorch", "mlops"],
        "about": "Design, train, and deploy ML systems at scale."
    },
    {
        "role": "DevOps Engineer",
        "skills": ["linux", "docker", "kubernetes", "ci/cd", "aws"],
        "about": "Automate infrastructure, CI/CD, and cloud deployments."
    },
    {
        "role": "Cloud Architect",
        "skills": ["aws", "azure", "gcp", "networking", "terraform"],
        "about": "Design and manage scalable cloud solutions."
    },
    {
        "role": "Cybersecurity Analyst",
        "skills": ["networking", "linux", "python", "security"],
        "about": "Protect systems and networks from cyber threats."
    },
    {
        "role": "Blockchain Developer",
        "skills": ["solidity", "ethereum", "smart contracts", "web3"],
        "about": "Build decentralized applications and smart contracts."
    },
    {
        "role": "Data Engineer",
        "skills": ["python", "sql", "spark", "etl", "airflow"],
        "about": "Design and maintain large-scale data pipelines."
    },
    {
        "role": "Mobile App Developer",
        "skills": ["kotlin", "swift", "flutter", "react native"],
        "about": "Build apps for Android and iOS platforms."
    },
    {
        "role": "Game Developer",
        "skills": ["c++", "unity", "unreal engine", "3d modeling"],
        "about": "Create interactive video games and simulations."
    },
    {
        "role": "Product Manager",
        "skills": ["communication", "strategy", "market research", "agile"],
        "about": "Define product vision, strategy, and manage delivery."
    },
    {
        "role": "UI/UX Designer",
        "skills": ["figma", "adobe xd", "prototyping", "usability testing"],
        "about": "Design user-centered interfaces and experiences."
    },
    {
        "role": "Digital Marketing Specialist",
        "skills": ["seo", "content", "analytics", "social media"],
        "about": "Promote products/services through digital channels."
    }
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
