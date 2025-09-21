import streamlit as st
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Mock Interview", page_icon="🧠", layout="wide")

# ---------- STYLING (Matches streamlit.py and styles the question container) ----------
st.markdown("""
<style>
:root {
    --primary: #4F46E5;
    --secondary: #6366F1;
    --accent: #A5B4FC;
    --muted: #6B7280;
    --text: #1F2937;
    --card-bg: #FFFFFF;
    --page-bg: linear-gradient(135deg, #F8FAFC 0%, #E0E7FF 100%);
    --shadow: 0 10px 30px rgba(15,23,42,0.1);
    --border-radius: 16px;
    --transition: all 0.3s ease;
}
body { 
    background: var(--page-bg); 
    font-family: 'Inter', sans-serif;
    color: var(--text);
}
.app-title { 
    font-size: 36px; 
    font-weight: 800; 
    color: var(--primary);
    text-align: center;
    margin-bottom: 24px;
}

/* This is the key change: Style the Streamlit container to look like a card */
.st-emotion-cache-1r4qj8v {
    width: 70%;
    margin: 20px auto;
    background: var(--card-bg);
    border: none;
    border-radius: var(--border-radius);
    padding: 2rem;
    box-shadow: var(--shadow);
}

.q-text {
    font-size: 40px;
    font-weight: 600;
    color: #6a5acd;
    margin-bottom: 1.5rem;
    line-height: 1.5;
    text-align: left;
}
.q-progress {
    font-size: 14px;
    color: var(--muted);
    text-align: right;
    margin-top: -15px;
    opacity: 0.8;
}
.stButton > button {
    width: 100%;
    border-radius: var(--border-radius);
    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    font-weight: 600;
    padding: 12px 24px;
    border: none;
    transition: var(--transition);
}
.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-2px);
}
.stRadio > div {
    gap: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ---------- QUESTION BANK (MCQ Format) ----------
QUESTIONS = {
    "AI Engineer": [
        {"question": "What is the primary purpose of a validation set in model training?", "options": ["To train the final model", "To tune hyperparameters", "To test the model after training", "To provide initial data"], "answer": "To tune hyperparameters"},
        {"question": "Which activation function is most commonly used for output layers in binary classification problems?", "options": ["ReLU", "Tanh", "Sigmoid", "Softmax"], "answer": "Sigmoid"},
        {"question": "What does the term 'overfitting' mean in machine learning?", "options": ["The model performs poorly on training data.", "The model is too simple to capture the data's complexity.", "The model performs well on training data but poorly on unseen data.", "The model has not been trained for enough epochs."], "answer": "The model performs well on training data but poorly on unseen data."},
        # ... add more questions to reach 15
    ],
    "Data Scientist": [
        {"question": "What is the main difference between classification and regression?", "options": ["Classification predicts continuous values, regression predicts discrete classes.", "Classification predicts discrete classes, regression predicts continuous values.", "Both predict continuous values.", "Both predict discrete classes."], "answer": "Classification predicts discrete classes, regression predicts continuous values."},
        {"question": "Which of these is a measure of central tendency?", "options": ["Standard Deviation", "Variance", "Range", "Median"], "answer": "Median"},
        {"question": "In A/B testing, what is the purpose of the p-value?", "options": ["To determine the sample size.", "To measure the effect size of the change.", "To determine the statistical significance of the results.", "To set the budget for the test."], "answer": "To determine the statistical significance of the results."},
        # ... add more questions to reach 15
    ],
    # Add other roles as needed
}

# ---------- App Logic ----------

st.markdown("<div class='app-title'>🧠 AI Mock Interview</div>", unsafe_allow_html=True)

# --- State Initialization ---
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.user_answers = []

role = st.session_state.get("chosen_career", "Data Scientist")
all_questions_for_role = QUESTIONS.get(role, QUESTIONS["Data Scientist"])

# --- Difficulty Selection View ---
if not st.session_state.interview_started:
    st.subheader(f"Prepare for your {role} Interview")
    
    difficulty_options = {
        "Easy (5 questions)": 5,
        "Medium (10 questions)": 10,
        "Hard (15 questions)": 15
    }
    selected_diff = st.selectbox("Select Difficulty", difficulty_options.keys())
    num_questions = difficulty_options[selected_diff]
    
    if st.button("Start Interview"):
        random.shuffle(all_questions_for_role)
        st.session_state.questions = all_questions_for_role[:num_questions]
        st.session_state.interview_started = True
        st.rerun()

# --- Question View ---
elif st.session_state.q_index < len(st.session_state.get("questions", [])):
    questions = st.session_state.questions
    q_data = questions[st.session_state.q_index]
    
    # Use st.container with a border to create the card, styled by the CSS above
    with st.container(border=True):
        st.markdown(f"<p class='q-progress'>Question {st.session_state.q_index + 1} / {len(questions)}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='q-text'>{q_data['question']}</p>", unsafe_allow_html=True)

        user_choice = st.radio(
            "Select your answer:",
            q_data["options"],
            key=f"q_{st.session_state.q_index}",
            index=None # No default selection
        )

        st.markdown("<br>", unsafe_allow_html=True) # Add some space before the button

        if st.button("Submit Answer ➡️"):
            if user_choice:
                st.session_state.user_answers.append(user_choice)
                if user_choice == q_data["answer"]:
                    st.session_state.score += 1
                
                st.session_state.q_index += 1
                st.rerun()
            else:
                st.warning("Please select an answer before submitting.")
        
# --- Results View ---
else:
    total_questions = len(st.session_state.get("questions", []))
    if total_questions > 0:
        final_score = (st.session_state.score / total_questions) * 100
        
        st.success(f"✅ Interview Completed! Your final score is: **{final_score:.1f}%**")
        
        with st.container(border=True):
            st.subheader("Your Performance")
            st.write(f"You correctly answered **{st.session_state.score}** out of **{total_questions}** questions.")

            if final_score >= 80:
                st.write("Excellent work! You have a strong grasp of the concepts.")
            elif final_score >= 50:
                st.write("Good effort! There are some areas where you can improve.")
            else:
                st.write("Keep practicing! Reviewing the fundamentals will help a lot.")

        st.balloons()

    # --- Controls to retry or go back ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Take Another Interview"):
            for key in ["interview_started", "q_index", "score", "user_answers", "questions"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with col2:
        if st.button("⬅️ Back to Career Advisor"):
            st.switch_page("streamlit.py")