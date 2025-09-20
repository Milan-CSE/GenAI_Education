# engine/advisor.py
def get_personalized_advice(profile, top_matches, use_mock=True):
    """
    Mock-first personalized advice. If use_mock=False and Gemini configured,
    it will attempt to call Gemini (not invoked by default).
    """
    if use_mock:
        interests = ", ".join(profile.get("interests", [])) or "AI, Tech"
        education = profile.get("education", "Undergraduate")
        career_goal = profile.get("career_goal", "AI Engineer")
        skills = ", ".join(profile.get("skills", [])) or "Python, SQL"

        advice = f"""
Personalized AI Career Guidance (Mock)

Name: {profile.get('name','')}
Age: {profile.get('age','')}
Education: {education}
Interests: {interests}
Career Goal: {career_goal}
Current Skills: {skills}

Suggested Path:
1. Focus on {interests.split(',')[0].strip()} fundamentals and core projects.
2. Build 2-3 portfolio projects using {skills.split(',')[0].strip()}.
3. Target internships / freelance projects to get hands-on experience.
4. Practice interviews and data-structure basics if applying to tech roles.

(Disclaimer: This is a mock response. Enable Gemini for richer AI output.)
"""
        return advice
    else:
        # Placeholder for real Gemini call (keep existing code in planner.py for reference)
        try:
            from google.generativeai import generativelanguage as genai
            prompt = f"Create personalized career advice for profile: {profile} and top matches: {top_matches}"
            model = genai.models.get("gemini-1.5-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error calling Gemini: {e}\n\nFalling back to mock advice.\n" + get_personalized_advice(profile, top_matches, use_mock=True)
