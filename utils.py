def clean_skills(skills):
    """Given list of strings or comma split, return cleaned lowercase skills."""
    return [s.strip().lower() for s in skills if isinstance(s, str) and s.strip()]
