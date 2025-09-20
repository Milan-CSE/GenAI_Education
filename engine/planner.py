import google.generativeai as genai

def generate_learning_plan(user_skills: list[str], target_role: str) -> str:
    prompt = f"""
    The user has these skills: {", ".join(user_skills)}.
    They want to become a {target_role}.
    Make a 3-month step-by-step learning roadmap with milestones.
    Show clear weekly tasks and goals.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text
