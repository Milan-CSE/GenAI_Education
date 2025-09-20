def get_personalized_advice(profile, top_matches, use_mock=True):
    """
    Returns personalized career advice.
    If use_mock=True, returns a fake response instead of calling Gemini API.
    """
    if use_mock:
        interests = ", ".join(profile.get("interests", [])) or "AI, Tech"
        education = profile.get("education", "Undergraduate")
        career_goal = profile.get("career_goal", "AI Engineer")
        skills = ", ".join(profile.get("skills", [])) or "Python, SQL"

        advice = f"""
        🎯 Personalized AI Career Guidance (Mock)

        Name: {profile.get('name', 'John Doe')}
        Age: {profile.get('age', '25')}
        Education: {education}
        Interests: {interests}
        Career Goal: {career_goal}
        Current Skills: {skills}

        Suggested Path:
        1. Learn advanced topics in {interests.split(',')[0]}
        2. Build projects in {skills.split(',')[0]} to strengthen your portfolio
        3. Apply to internships or entry-level roles towards your career goal: {career_goal}
        4. Keep updating skills as per industry trends

        Note: This is a mock response. Real AI advice requires Gemini API.
        """
        return advice
    else:
        from google.generativeai import generativelanguage as genai
        prompt = f"Create personalized career advice based on {profile} and matches {top_matches}"
        model = genai.models.get("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
