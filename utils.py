# utils.py
def clean_skills(skills):
    return [s.strip().lower() for s in skills if s.strip()]
