import streamlit as st
from io import BytesIO
import pdfplumber
import re
import json
import requests

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from engine.matcher import match_careers
from engine.advisor import get_personalized_advice
from engine.planner import generate_learning_plan

from github_extractor import extract_github_skills

from ui_components import show_career_card
from utils import clean_skills

from engine.advisor import get_personalized_advice

def collect_user_profile(prefill=None):
    if prefill is None:
        prefill = {}
    name = st.text_input("Name", value=prefill.get("name", ""), help="Enter your full name")
    age = st.number_input("Age", min_value=18, max_value=99, value=prefill.get("age", 25), step=1)
    gender_options = ["Male", "Female", "Prefer not to say"]
    gender_index = gender_options.index(prefill.get("gender", "Prefer not to say")) if prefill.get("gender") in gender_options else 2
    gender = st.selectbox("Gender", gender_options, index=gender_index, help="Select your gender")
    education_options = ["High School", "Undergraduate", "Graduate", "Postgraduate", "PhD"]
    education_index = education_options.index(prefill.get("education", "Graduate")) if prefill.get("education") in education_options else 2
    education = st.selectbox("Education", education_options, index=education_index, help="Your highest education level")
    experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=prefill.get("experience", 0), step=1)
    career_goal = st.text_input("Career Goal", value=prefill.get("career_goal", ""), help="Your desired career path")
    return {
        "name": name,
        "age": age,
        "gender": gender,
        "education": education,
        "experience": experience,
        "career_goal": career_goal
    }

# ---------- Page setup ----------
st.set_page_config(page_title="AI Career Advisor", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# ---------- Enhanced CSS / Styling ----------
st.markdown("""
<style>
:root {
  --primary: #2E7D7D; /* Deep Teal */
  --secondary: #4A9A9A; /* Lighter Teal */
  --accent: #FF6F61; /* Coral Accent */
  --background: #F5F5F0; /* Soft Cream */
  --text-primary: #1A3C3C; /* Dark Teal for text */
  --card-bg: #FFFFFF; /* Pure White for cards */
  --shadow: 0 4px 20px rgba(46, 125, 125, 0.1);
  --border-radius: 12px;
  --transition: all 0.3s ease;
  --font-family: 'Poppins', sans-serif;
}
body {
  background: var(--background);
  font-family: var(--font-family);
  color: var(--text-primary);
}
.app-title {
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  margin-bottom: 12px;
  letter-spacing: -1px;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}
.app-sub {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 500;
  opacity: 0.9;
}
.role-card {
  border-radius: var(--border-radius);
  padding: 20px;
  background: var(--card-bg);
  box-shadow: var(--shadow);
  transition: var(--transition);
  cursor: pointer;
  border: 1px solid rgba(46, 125, 125, 0.1);
}
.role-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 6px 25px rgba(46, 125, 125, 0.2);
  background: linear-gradient(135deg, var(--card-bg) 0%, #F9FBFA 100%);
}
.match-score {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 10px;
}
.role-about {
  font-size: 15px;
  color: var(--text-primary);
  line-height: 1.6;
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
  font-family: var(--font-family);
  box-shadow: 0 2px 10px rgba(46, 125, 125, 0.2);
}
.stButton > button:hover {
  opacity: 0.95;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(46, 125, 125, 0.3);
}
.stTextInput > div > div > input {
  border-radius: var(--border-radius);
  border: 1px solid var(--secondary);
  padding: 12px;
  font-size: 16px;
  transition: var(--transition);
  background: #FAFAF9;
  color: var(--text-primary);
}
.stTextInput > div > div > input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(46, 125, 125, 0.1);
}
.stFileUploader > div > button {
  border-radius: var(--border-radius);
  background: var(--accent);
  color: var(--text-primary);
  font-weight: 500;
  font-family: var(--font-family);
}
.stSpinner > div {
  color: var(--primary);
}
.card {
  border-radius: var(--border-radius);
  padding: 16px;
  background: var(--card-bg);
  box-shadow: var(--shadow);
}
.stDivider {
  margin: 30px 0;
  border-color: var(--secondary);
  opacity: 0.5;
}
.stExpander {
  border-radius: var(--border-radius);
  border: 1px solid var(--secondary);
  overflow: hidden;
  background: #FAFAF9;
}
.stExpander > summary {
  padding: 16px;
  font-weight: 600;
  color: var(--text-primary);
  background: var(--card-bg);
  transition: var(--transition);
}
.stExpander:hover > summary {
  background: #F9FBFA;
}
.main-card {
  background: var(--card-bg);
  border-radius: var(--border-radius);
  padding: 2rem;
  margin: 20px auto;
  width: 70%;
  box-shadow: var(--shadow);
  text-align: center;
  color: var(--text-primary) !important;
}
.role-heading {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.q-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.q-text {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}
.q-progress {
  font-size: 14px;
  color: var(--text-primary);
  text-align: right;
  margin-top: -15px;
  opacity: 0.7;
}
.stTextArea > div > div > textarea {
  border-radius: var(--border-radius);
  border: 1px solid var(--secondary);
  padding: 12px;
  font-size: 16px;
  background: #FAFAF9;
  color: var(--text-primary);
}
.stTextArea > div > div > textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(46, 125, 125, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Load Google Fonts (Poppins)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Initialize view state
if "view" not in st.session_state:
    st.session_state.view = "advisor"

# Load skills DB
with open("skills_database.json", "r") as f:
    SKILL_DB = json.load(f)

# Detect skills function
def detect_skills(text: str, skills_db: list[str]) -> list[str]:
    text_lower = text.lower()
    found = []
    for skill in skills_db:
        pattern = r"\b" + re.escape(skill.lower()).replace(r"\ ", r"[\s-]") + r"\b"
        if re.search(pattern, text_lower, flags=re.IGNORECASE):
            found.append(skill.lower())
    return found

# Extract GitHub skills
def extract_github_skills(username: str, skills_db: list[str]) -> list[str]:
    skills_found = set()
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos = requests.get(repos_url, headers=headers).json()
    if isinstance(repos, dict) and repos.get("message"):
        return []
    for repo in repos:
        lang_url = repo.get("languages_url")
        if lang_url:
            langs = requests.get(lang_url, headers=headers).json()
            for lang in langs.keys():
                lang_norm = lang.lower()
                if lang_norm in ["jupyter notebook"]:
                    lang_norm = "python"
                if lang_norm in [s.lower() for s in skills_db]:
                    skills_found.add(lang_norm)
        for topic in repo.get("topics", []):
            topic_norm = topic.lower()
            if topic_norm in [s.lower() for s in skills_db]:
                skills_found.add(topic_norm)
    return list(skills_found)

# QUESTION BANK
QUESTIONS = {
    "Data Scientist": ["Explain the Difference Between Classification and Regression?", "What is Bias in Machine Learning?", "What is Cross-Validation?", "What are Support Vectors in SVM?", "Explain SVM Algorithm in Detail", "What is PCA? When do you use it?", "What is ‘Naive’ in a Naive Bayes?", "What is Unsupervised Learning?", "What is Supervised Learning?", "What are Different Types of Machine Learning algorithms?", "What is F1 score? How would you use it?", "Define Precision and Recall?", "How to Tackle Overfitting and Underfitting?", "What is a Neural Network?", "What are Loss Function and Cost Functions? Explain the key Difference Between them?"],
    "AI Engineer": ["What are the main types of AI?", "How does machine learning differ from traditional programming?", "What is a Neural Network?", "What are Loss Function and Cost Functions? Explain the key Difference Between them?", "What is Ensemble learning?", "How to do you make sure which Machine Learning Algorithm to use?", "How to Handle Outlier Values?", "What is a Random Forest? How does it work?", "What is Collaborative Filtering? And Content-Based Filtering?", "What is Clustering?", "How can you select K for K-means Clustering?", "What are Recommender Systems?", "Can logistic regression use for more than 2 classes?", "Explain Correlation and Covariance?", "What is P-value?"],
    # Add other roles as needed...
}

# ---------- Advisor View ----------
if st.session_state.view == "advisor":
    st.sidebar.header("⚙️ Settings & Samples")
    enable_gemini = st.sidebar.checkbox("🔑 Enable Gemini (one-time test)", value=False)
    st.sidebar.markdown("**Load sample profile:**")
    sample_choice = st.sidebar.selectbox("Pick a sample profile", ["None", "Alice (Data Scientist)", "Bob (AI Engineer)", "Charlie (Career Switcher)"])

    SAMPLES = {
        "Alice (Data Scientist)": {"name": "Alice", "age": 24, "gender": "Female", "education": "Graduate", "experience": 1, "career_goal": "Data Scientist", "skills": ["python", "sql", "statistics"]},
        "Bob (AI Engineer)": {"name": "Bob", "age": 28, "gender": "Male", "education": "Postgraduate", "experience": 4, "career_goal": "AI Engineer", "skills": ["python", "deep learning", "tensorflow"]},
        "Charlie (Career Switcher)": {"name": "Charlie", "age": 35, "gender": "Male", "education": "Postgraduate", "experience": 10, "career_goal": "Product Manager", "skills": ["communication", "excel", "strategy"]}
    }

    if sample_choice != "None":
        st.sidebar.success(f"Loaded sample: {sample_choice}")
        st.session_state["profile"] = SAMPLES[sample_choice]

    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with Streamlit • Powered by AI")

    st.markdown("<div class='app-title'>🎯 AI Career & Skills Advisor</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-sub'>Discover your path with personalized insights</div>", unsafe_allow_html=True)
    st.divider()

    st.subheader("📄 Upload Resume (optional)")
    uploaded_resume = st.file_uploader("Upload your resume as PDF", type=["pdf"], help="Upload a PDF to extract skills")

    st.subheader("🌐 Import from GitHub (optional)")
    github_username = st.text_input("Enter your GitHub username", help="Link your GitHub to analyze skills")

    github_skills = []
    if github_username:
        with st.spinner("Fetching skills from GitHub..."):
            try:
                github_skills = extract_github_skills(github_username, SKILL_DB)
                if github_skills:
                    st.success(f"✅ Found {len(github_skills)} skills from GitHub!")
                    st.write(", ".join(github_skills))
                    if "profile" not in st.session_state:
                        st.session_state["profile"] = {}
                    st.session_state["profile"]["skills"] = list(set(st.session_state["profile"].get("skills", []) | set(github_skills)))
                else:
                    st.warning("No matching skills found in GitHub profile.")
            except Exception as e:
                st.error(f"Error fetching GitHub data: {e}")

    parsed_profile = None
    if uploaded_resume is not None:
        with pdfplumber.open(uploaded_resume) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        detected_skills = detect_skills(text, SKILL_DB)
        parsed_profile = {
            "name": text.split("\n")[0] if text else "Unknown",
            "age": 25,
            "gender": "Prefer not to say",
            "education": "Graduate",
            "experience": 0,
            "career_goal": "Not specified",
            "skills": detected_skills
        }
        st.success("Resume uploaded & parsed successfully! ✅")
        st.json(parsed_profile)
        st.session_state["profile"] = parsed_profile

    merged_profile = {}
    if parsed_profile and github_skills:
        merged_profile = {**parsed_profile}
        merged_profile["skills"] = list(set(parsed_profile.get("skills", []) + github_skills))
    elif parsed_profile:
        merged_profile = parsed_profile
    elif github_skills:
        merged_profile = {
            "name": st.session_state.get("profile", {}).get("name", "Unknown"),
            "age": 25,
            "gender": "Prefer not to say",
            "education": "Graduate",
            "experience": 0,
            "career_goal": "Not specified",
            "skills": github_skills
        }

    if merged_profile:
        prefill = merged_profile
        with st.expander("👤 Edit loaded profile (Resume/GitHub)", expanded=True):
            profile = collect_user_profile(prefill=prefill)
            if "skills" in prefill:
                profile["skills"] = prefill["skills"]
    elif "profile" in st.session_state:
        prefill = st.session_state.get("profile", {})
        source = "Sample" if st.session_state.get("profile_from") == "sample" else "Manual"
        with st.expander(f"👤 Edit loaded profile ({source})", expanded=True):
            profile = collect_user_profile(prefill=prefill)
            if "skills" in prefill:
                profile["skills"] = prefill["skills"]
    else:
        profile = collect_user_profile()

    skills_input = st.text_input("Your Skills", placeholder="e.g., Python, SQL, Machine Learning", value=", ".join(profile.get("skills", [])), help="List your skills separated by commas")
    user_skills = clean_skills([s for s in skills_input.split(",") if s.strip()])
    profile["skills"] = user_skills

    @st.cache_data(ttl=300)
    def cached_match(skills_tuple):
        skills_list = list(skills_tuple)
        return match_careers(skills_list)

    col1, col2 = st.columns([1, 3])
    with col1:
        analyze = st.button("🚀 Analyze My Career Path", use_container_width=True, help="Click to start analysis")

    result_holder = st.container()
    advice_holder = st.container()
    controls_holder = st.container()

    if analyze:
        if not user_skills:
            st.warning("Please enter skills to analyze.")
        else:
            with st.spinner("Analyzing your career path..."):
                matches = cached_match(tuple(user_skills))
            st.session_state["analysis"] = {"profile": profile, "matches": matches}
            advice = get_personalized_advice(profile, matches[:3], use_mock=not enable_gemini)
            st.session_state["advice"] = advice

    if "analysis" in st.session_state:
        matches = st.session_state["analysis"]["matches"]
        profile = st.session_state["analysis"]["profile"]
        with result_holder:
            st.subheader("📌 Top 3 Career Matches")
            cols = st.columns(3)
            for i, m in enumerate(matches[:3]):
                role = m["role"]
                with cols[i]:
                    if st.button(f"🎯 {role}", key=f"role_card_{i}", help=f"Start mock interview for {role}"):
                        st.session_state["chosen_career"] = role
                        st.session_state.view = "interview"
                        st.rerun()
                    st.markdown(
                        f"""
                        <div class='role-card'>
                            <div class='match-score'>Match: {m['match']}%</div>
                            <div class='role-about'>{m['about'][:120]}...</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with advice_holder:
            st.subheader("✨ Personalized AI Career Guidance")
            if "advice" in st.session_state:
                st.text(st.session_state["advice"])
            else:
                with st.spinner("Generating advice..."):
                    advice = get_personalized_advice(profile, matches[:3], use_mock=not enable_gemini)
                    st.session_state["advice"] = advice
                    st.text(advice)

        with controls_holder:
            def export_pdf_bytes(profile_obj, matches_obj, advice_text):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []
                elements.append(Paragraph("AI Career Advisor Report", styles["Title"]))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("👤 User Profile", styles["Heading2"]))
                for k, v in profile_obj.items():
                    display_v = ", ".join(v) if isinstance(v, list) else str(v)
                    elements.append(Paragraph(f"<b>{k.capitalize()}:</b> {display_v}", styles["Normal"]))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("📌 Top Career Matches", styles["Heading2"]))
                for m in matches_obj[:3]:
                    elements.append(Paragraph(f"<b>{m['role']}</b> — {m['match']}% match", styles["Normal"]))
                    elements.append(Paragraph(m["about"], styles["Normal"]))
                    if m.get("missing"):
                        elements.append(Paragraph("Missing Skills: " + ", ".join(m["missing"]), styles["Normal"]))
                    elements.append(Spacer(1, 6))
                elements.append(Paragraph("✨ Personalized Advice", styles["Heading2"]))
                for line in advice_text.splitlines():
                    if line.strip():
                        elements.append(Paragraph(line.strip(), styles["Normal"]))
                elements.append(Spacer(1, 8))
                doc.build(elements)
                buffer.seek(0)
                return buffer.getvalue()

            pdf_bytes = export_pdf_bytes(st.session_state["analysis"]["profile"], st.session_state["analysis"]["matches"], st.session_state["advice"])
            st.download_button("📥 Export Report as PDF", data=pdf_bytes, file_name="career_advisor_report.pdf", mime="application/pdf", help="Download your personalized report")

    if "analysis" not in st.session_state:
        st.info("Fill your profile and skills, then click **Analyze** to begin.")

# ---------- Interview View ----------
else:
    st.sidebar.header("⚙️ Settings")
    enable_gemini = st.sidebar.checkbox("🔑 Enable Gemini for Evaluation", value=False)

    role = st.session_state.get("chosen_career", "Data Scientist")

    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.answers = []
        st.session_state.feedbacks = []
        st.session_state.scores = []

    if "difficulty" not in st.session_state:
        difficulty_options = ["Easy (5 questions)", "Medium (10 questions)", "Hard (15 questions)"]
        selected_diff = st.selectbox("Select Difficulty", difficulty_options, help="Choose the number of questions")
        if selected_diff == "Easy (5 questions)":
            st.session_state.num_questions = 5
        elif selected_diff == "Medium (10 questions)":
            st.session_state.num_questions = 10
        else:
            st.session_state.num_questions = 15
        st.session_state.difficulty = selected_diff

    if role in QUESTIONS:
        questions = QUESTIONS[role][:st.session_state.num_questions]
    else:
        questions = QUESTIONS["Data Scientist"][:st.session_state.num_questions]

    def evaluate_answer(question, answer, use_mock=True):
        if use_mock:
            correctness = 8
            communication = 7
            relevance = 9
            feedback = "Good answer. Could be more detailed."
        else:
            try:
                prompt = f"Evaluate the following answer to the question '{question}':\n\n{answer}\n\nProvide scores out of 10 for: Correctness, Communication, Relevance. Then, give brief feedback."
                advice = get_personalized_advice({}, [], use_mock=False)
                lines = advice.splitlines()
                correctness = int(lines[0].split(': ')[1])
                communication = int(lines[1].split(': ')[1])
                relevance = int(lines[2].split(': ')[1])
                feedback = '\n'.join(lines[3:])
            except:
                correctness, communication, relevance = 5, 5, 5
                feedback = "Error in evaluation. Using default scores."
        return {'correctness': correctness, 'communication': communication, 'relevance': relevance}, feedback

    if st.session_state.q_index < len(questions):
        q = questions[st.session_state.q_index]
        st.markdown(f"<p class='role-heading'>Mock Interview — {role}</p>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='main-card'>
                <p class='q-label'>Question {st.session_state.q_index + 1}</p>
                <p class='q-text'>{q}</p>
                <p class='q-progress'>{st.session_state.q_index + 1} / {len(questions)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        user_answer = st.text_area("Your Answer:", key=f"q_{st.session_state.q_index}", help="Provide your response here")
        if st.button("Submit Answer ➡️", help="Submit your answer for evaluation"):
            if user_answer:
                with st.spinner("Evaluating your response..."):
                    scores, feedback = evaluate_answer(q, user_answer, enable_gemini)
                    st.session_state.answers.append(user_answer)
                    st.session_state.feedbacks.append(feedback)
                    st.session_state.scores.append(scores)
                    st.session_state.q_index += 1
                    st.rerun()
            else:
                st.warning("⚠️ Please provide an answer before submitting.")
    else:
        if st.session_state.scores:
            avg_correctness = sum(s['correctness'] for s in st.session_state.scores) / len(st.session_state.scores)
            avg_communication = sum(s['communication'] for s in st.session_state.scores) / len(st.session_state.scores)
            avg_relevance = sum(s['relevance'] for s in st.session_state.scores) / len(st.session_state.scores)
            overall_score = (avg_correctness + avg_communication + avg_relevance) / 3

            st.success(f"✅ Interview Completed! Overall Score: {overall_score:.1f}/10")
            st.markdown("<div class='scorecard'>", unsafe_allow_html=True)
            st.subheader("Final Scorecard")
            st.write(f"Tech Skills / Correctness: {avg_correctness:.1f}/10")
            st.write(f"Communication: {avg_communication:.1f}/10")
            st.write(f"Relevance / Problem Solving: {avg_relevance:.1f}/10")
            st.write(f"Confidence Level: {'High' if overall_score > 8 else 'Medium' if overall_score > 5 else 'Low'}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("Feedback & Next Steps")
            weak_areas = []
            if avg_correctness < 7:
                weak_areas.append("Technical knowledge")
            if avg_communication < 7:
                weak_areas.append("Communication skills")
            if avg_relevance < 7:
                weak_areas.append("Relevance and problem-solving")

            if weak_areas:
                st.write("Weak areas identified: " + ", ".join(weak_areas))
                st.write("Suggested resources:")
                for area in weak_areas:
                    if area == "Technical knowledge":
                        st.write("- Recommended: Online courses on Coursera or edX.")
                    elif area == "Communication skills":
                        st.write("- Recommended: Practice with Toastmasters or mock interviews.")
                    else:
                        st.write("- Recommended: Read 'Cracking the PM Interview' or case studies.")
            else:
                st.write("Strong performance! Consider senior roles or specializations.")
            st.balloons()

        if st.button("🔄 Retry Interview", help="Start the interview again"):
            st.session_state.q_index = 0
            st.session_state.answers = []
            st.session_state.feedbacks = []
            st.session_state.scores = []
            del st.session_state.difficulty
            st.rerun()

        if st.button("⬅️ Back to Career Advisor", help="Return to the main advisor page"):
            st.session_state.view = "advisor"
            st.rerun()