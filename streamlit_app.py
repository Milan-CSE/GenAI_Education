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
from user_profile import collect_user_profile
from github_extractor import extract_github_skills

from ui_components import show_career_card
from utils import clean_skills

def collect_user_profile(prefill=None):
    if prefill is None:
        prefill = {}
    name = st.text_input("Name", value=prefill.get("name", ""))
    age = st.number_input("Age", min_value=18, max_value=99, value=prefill.get("age", 25), step=1)
    gender_options = ["Male", "Female", "Prefer not to say"]
    gender_index = gender_options.index(prefill.get("gender", "Prefer not to say")) if prefill.get("gender") in gender_options else 2
    gender = st.selectbox("Gender", gender_options, index=gender_index)
    education_options = ["High School", "Undergraduate", "Graduate", "Postgraduate", "PhD"]
    education_index = education_options.index(prefill.get("education", "Graduate")) if prefill.get("education") in education_options else 2
    education = st.selectbox("Education", education_options, index=education_index)
    experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=prefill.get("experience", 0), step=1)
    career_goal = st.text_input("Career Goal", value=prefill.get("career_goal", ""))
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

# ---------- CSS / Styling ----------
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
}
.app-title { 
  font-size: 42px; 
  font-weight: 900; 
  background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center; 
  margin-bottom: 8px; 
  letter-spacing: -0.5px;
}
.app-sub { 
  text-align: center; 
  color: var(--muted); 
  margin-bottom: 24px; 
  font-size: 18px;
  font-weight: 500;
}
.role-card { 
  border-radius: var(--border-radius); 
  padding: 24px; 
  background: var(--card-bg); 
  box-shadow: var(--shadow); 
  transition: var(--transition);
  cursor: pointer;
}
.role-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(15,23,42,0.15);
}
.small { 
  font-size: 14px; 
  color: var(--muted); 
  font-weight: 400;
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

.st-emotion-cache-1r4qj8v {
    background-color: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
}
.stTextInput > div > div > input {
  border-radius: var(--border-radius);
  border: 1px solid var(--accent);
  padding: 12px;
  transition: var(--transition);
}
.stTextInput > div > div > input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
}
.stFileUploader > div > button {
  border-radius: var(--border-radius);
  background: var(--accent);
  color: var(--text);
  font-weight: 500;
}
.stSpinner > div {
  color: var(--primary);
}
.card {
  border-radius: var(--border-radius);
  padding: 16px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.5), 0 1px 2px rgba(0,0,0,0.05);
}
.match-score {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
}
.role-about {
  font-size: 14px;
  color: var(--text);
  line-height: 1.5;
}
.stDivider {
  margin: 24px 0;
  border-color: var(--accent);
}
.stExpander {
  border-radius: var(--border-radius);
  border: 1px solid var(--accent);
  overflow: hidden;
}
.stExpander > summary {
  padding: 16px;
  font-weight: 600;
  color: var(--text);
  background: var(--card-bg);
}
</style>
""", unsafe_allow_html=True)



# ---------- Sidebar: samples + settings ----------
st.sidebar.header("⚙️ Settings & Samples")
enable_gemini = st.sidebar.checkbox("🔑 Enable Gemini (one-time test)", value=False)
st.sidebar.markdown("**Load sample profile:**")
sample_choice = st.sidebar.selectbox("Pick a sample profile", ["None", "Alice (Data Scientist)", "Bob (AI Engineer)", "Charlie (Career Switcher)"])

SAMPLES = {
    "Alice (Data Scientist)": {
        "name": "Alice", "age": 24, "gender": "Female", "education": "Graduate",
        "experience": 1, "career_goal": "Data Scientist", "skills": ["python","sql","statistics"]
    },
    "Bob (AI Engineer)": {
        "name": "Bob", "age": 28, "gender": "Male", "education": "Postgraduate",
        "experience": 4, "career_goal": "AI Engineer", "skills": ["python","deep learning","tensorflow"]
    },
    "Charlie (Career Switcher)": {
        "name": "Charlie", "age": 35, "gender": "Male", "education": "Postgraduate",
        "experience": 10, "career_goal": "Product Manager",  "skills": ["communication","excel","strategy"]
    }
}


if sample_choice != "None":
    st.sidebar.success(f"Loaded sample: {sample_choice}")
    st.session_state["profile"] = SAMPLES[sample_choice]

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit • Local mock AI by default")

# ---------- Top header ----------
st.markdown("<div class='app-title'>🎯 AI Career & Skills Advisor</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub'>Map your skills → roles → step-by-step career roadmap</div>", unsafe_allow_html=True)
st.divider()



# Load your skills database (JSON file)
with open("skills_database.json", "r") as f:
    SKILL_DB = json.load(f)   # Example: ["python", "c++", "tensorflow", "machine learning", "sql", "excel"]

def detect_skills(text: str, skills_db: list[str]) -> list[str]:
    """
    Detect skills from resume text using regex (case-insensitive).
    Allows flexible matches (e.g., 'C++', 'TensorFlow 2.0', 'machine-learning').
    """
    text_lower = text.lower()
    found = []

    for skill in skills_db:
        # Build regex pattern for each skill
        # \b ensures word boundaries (exact match)
        # also allow hyphen/space variations (e.g., "machine-learning")
        pattern = r"\b" + re.escape(skill.lower()).replace(r"\ ", r"[\s-]") + r"\b"

        if re.search(pattern, text_lower, flags=re.IGNORECASE):
            found.append(skill.lower())

    return found



#-----------extract skills from GitHub ----------

def extract_github_skills(username: str, skills_db: list[str]) -> list[str]:
    """
    Extracts skills from a user's GitHub repos using GitHub API.
    Looks at repo languages + topics, and cross-matches with skills_db.
    """
    skills_found = set()
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}  # enable topics API

    repos_url = f"https://api.github.com/users/{username}/repos"
    repos = requests.get(repos_url, headers=headers).json()

    if isinstance(repos, dict) and repos.get("message"):
        return []

    for repo in repos:
        # Languages
        lang_url = repo.get("languages_url")
        if lang_url:
            langs = requests.get(lang_url, headers=headers).json()
            for lang in langs.keys():
                lang_norm = lang.lower()
                # map special cases
                if lang_norm in ["jupyter notebook"]:
                    lang_norm = "python"
                if lang_norm in [s.lower() for s in skills_db]:
                    skills_found.add(lang_norm)

        # Topics
        for topic in repo.get("topics", []):
            topic_norm = topic.lower()
            if topic_norm in [s.lower() for s in skills_db]:
                skills_found.add(topic_norm)

    return list(skills_found)




# ---------- Resume Upload ----------
st.subheader("📄 Upload Resume")
uploaded_resume = st.file_uploader("Upload your resume as PDF", type=["pdf"])



# ---------- GitHub Input ----------
with st.container(border=True):
    st.subheader("🌐 Import from GitHub (optional)")
    github_username = st.text_input(
        "Enter your GitHub username to extract technical skills.", 
        placeholder="e.g., octocat", 
        label_visibility="collapsed"
    )

# Initialize empty list so it's always defined
github_skills = []

if github_username:
    with st.spinner("Fetching skills from GitHub..."):
        try:
            github_skills = extract_github_skills(github_username, SKILL_DB)
            if github_skills:
                st.success(f"✅ Found {len(github_skills)} skills from GitHub!")
                st.write(", ".join(github_skills))
                # Merge into profile
                if "profile" not in st.session_state:
                    st.session_state["profile"] = {}
                st.session_state["profile"]["skills"] = list(
                    set(st.session_state["profile"].get("skills", [])) | set(github_skills)
                )
            else:
                st.warning("No matching skills found in GitHub profile.")
        except Exception as e:
            st.error(f"Error fetching GitHub data: {e}")




parsed_profile = None
if uploaded_resume is not None:
    with pdfplumber.open(uploaded_resume) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Detect skills using regex
    detected_skills = detect_skills(text, SKILL_DB)


    parsed_profile = {
        "name": text.split("\n")[0] if text else "Unknown",
        "age": 25,   # placeholder
        "gender": "Prefer not to say",
        "education": "Graduate",
        "experience": 0,
        "career_goal": "Not specified",
        "skills": detected_skills
    }

    st.success("Resume uploaded & parsed successfully! ✅")
    



# ---------- Profile form ----------
merged_profile = {}



# Merge Resume + GitHub if both available
if parsed_profile and github_skills:
    merged_profile = {**parsed_profile}
    merged_profile["skills"] = list(set(parsed_profile.get("skills", []) + github_skills))
elif parsed_profile:
    merged_profile = parsed_profile
elif github_skills:
    merged_profile = {
        "name": st.session_state.get("profile", {}).get("name", "Unknown"),
        "age": 25,  # placeholder
        "gender": "Prefer not to say",
        "education": "Graduate",
        "experience": 0,
        "career_goal": "Not specified",
        "skills": github_skills
    }



# Priority order: Resume+GitHub → Resume → GitHub → Sample → Manual 
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



# Skills input (single-line, comma separated)
skills_input = st.text_input("Your Skills", placeholder="Python, SQL, Machine Learning", value=", ".join(profile.get("skills", [])))
user_skills = clean_skills([s for s in skills_input.split(",") if s.strip()])
profile["skills"] = user_skills

# ---------- Helpers: caching match results for speed ----------
@st.cache_data(ttl=300)
def cached_match(skills_tuple):
    # cache key uses tuple of skills
    skills_list = list(skills_tuple)
    return match_careers(skills_list)

# ---------- Analyze button ----------
col1, col2 = st.columns([1, 3])
with col1:
    analyze = st.button("🚀 Analyze My Career Path", use_container_width=True)

# Result containers
result_holder = st.container()
advice_holder = st.container()
controls_holder = st.container()

if analyze:
    if not user_skills:
        st.warning("Please enter skills to analyze.")
    else:
        # get matches (cached)
        matches = cached_match(tuple(user_skills))

        # persist into session for later (pdf download etc.)
        st.session_state["analysis"] = {
            "profile": profile,
            "matches": matches
        }

        # ---------- Show Top 3 Matches as cards ----------
        with result_holder:
            st.subheader("📌 Top 3 Career Matches")
            cols = st.columns(3)

            for i, m in enumerate(matches[:3]):
                role = m["role"]

                with cols[i]:
                    
                    # Use a container to group the button and the card content
                    with st.container():

                        # The button now contains all the card's visual elements
                        if st.button(
                            label=f"🎯 {role}",
                            key=f"role_card_{i}",
                            use_container_width=True
                        ):
                            st.session_state["chosen_career"] = role
                            st.switch_page("pages/1_interview.py")

                        # -------- card display --------
                        st.markdown(
                            f"""
                            <div class="role-card">
                                <div class="match-score">Match: {m['match']}%</div>
                                <div class="role-about">{m['about'][:120]}...</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )       

                    
        # ---------- Personalized Advice (mock or Gemini one-time) ----------
        with advice_holder:
            st.subheader("✨ Personalized AI Career Guidance")
            with st.spinner("Thinking..."):
                advice = get_personalized_advice(profile, matches[:3], use_mock=not enable_gemini)
            st.text(advice)

        # ---------- Download / Export controls ----------
        with controls_holder:
            def export_pdf_bytes(profile_obj, matches_obj, advice_text):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(Paragraph("AI Career Advisor Report", styles["Title"]))
                elements.append(Spacer(1, 8))

                # Profile
                elements.append(Paragraph("👤 User Profile", styles["Heading2"]))
                for k, v in profile_obj.items():
                    display_v = ", ".join(v) if isinstance(v, list) else str(v)
                    elements.append(Paragraph(f"<b>{k.capitalize()}:</b> {display_v}", styles["Normal"]))
                elements.append(Spacer(1, 8))

                # Matches
                elements.append(Paragraph("📌 Top Career Matches", styles["Heading2"]))
                for m in matches_obj[:3]:
                    elements.append(Paragraph(f"<b>{m['role']}</b> — {m['match']}% match", styles["Normal"]))
                    elements.append(Paragraph(m["about"], styles["Normal"]))
                    if m.get("missing"):
                        elements.append(Paragraph("Missing Skills: " + ", ".join(m["missing"]), styles["Normal"]))
                    elements.append(Spacer(1, 6))

                elements.append(Paragraph("✨ Personalized Advice", styles["Heading2"]))
                # Break advice into paragraphs
                for line in advice_text.splitlines():
                    if line.strip():
                        elements.append(Paragraph(line.strip(), styles["Normal"]))
                elements.append(Spacer(1, 8))

                doc.build(elements)
                buffer.seek(0)
                return buffer.getvalue()

            if "analysis" in st.session_state:
                pdf_bytes = export_pdf_bytes(st.session_state["analysis"]["profile"], st.session_state["analysis"]["matches"], advice)
                st.download_button("📥 Export Report as PDF", data=pdf_bytes, file_name="career_advisor_report.pdf", mime="application/pdf")
            else:
                st.info("Run analysis to enable export.")

# If not analyzed yet, show a friendly sample preview
if "analysis" not in st.session_state:
    st.info("Fill your profile and skills, then click **Analyze** to see tailored matches and a learning plan.")