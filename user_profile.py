import streamlit as st

def collect_user_profile(prefill: dict | None = None) -> dict:
    """
    Collects user profile. If prefill dict provided, populate default values.
    Returns a profile dict and saves into st.session_state['profile'].
    """
    st.subheader("👤 Your Profile")
    col1, col2 = st.columns(2)

    if prefill is None:
        prefill = {}

    with col1:
        name = st.text_input("Full Name", value=prefill.get("name", ""))
        age = st.number_input("Age", min_value=10, max_value=80, step=1, value=prefill.get("age", 22))
        gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"], index=0 if not prefill.get("gender") else ["Prefer not to say","Male","Female","Other"].index(prefill.get("gender")))
        

    with col2:
        education = st.selectbox("Education Level", ["High School", "Undergraduate", "Graduate", "Postgraduate", "Other"], index=0 if not prefill.get("education") else ["High School","Undergraduate","Graduate","Postgraduate","Other"].index(prefill.get("education")))
        experience = st.slider("Years of Experience", 0, 30, value=prefill.get("experience", 0))
        career_goal = st.text_input("Career Goal (e.g. AI Engineer)", value=prefill.get("career_goal", ""))


    profile = {
        "name": name,
        "age": age,
        "gender": gender,
        "education": education,
        "experience": experience,
        "career_goal": career_goal,
        
        # skills will be attached in streamlit main after skills input
    }

    st.session_state["profile"] = profile
    return profile
