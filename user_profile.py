import streamlit as st

def collect_user_profile():
    st.subheader("👤 Your Profile")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=10, max_value=80, step=1)
            gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
            interests = st.text_input("Your Interests (comma separated)", placeholder="AI, Robotics, Finance")

        with col2:
            education = st.selectbox("Education Level", [
                "High School", "Undergraduate", "Graduate", "Postgraduate", "Other"
            ])
            experience = st.slider("Years of Experience", 0, 20, 0)
            career_goal = st.text_input("Your Career Goal (e.g. AI Engineer)")

    # Convert interests to list
    interests_list = [i.strip() for i in interests.split(",") if i.strip()]

    # Save in session state
    st.session_state["profile"] = {
        "name": name,
        "age": age,
        "gender": gender,
        "education": education,
        "experience": experience,
        "career_goal": career_goal,
        "interests": interests_list
    }

    return st.session_state["profile"]
