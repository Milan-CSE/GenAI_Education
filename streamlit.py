import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from user_profile import collect_user_profile
from engine.matcher import match_careers
from engine.advisor import get_personalized_advice
from engine.planner import generate_learning_plan

from ui_components import show_career_card
from utils import clean_skills

# ---------- Page setup ----------
st.set_page_config(page_title="AI Career Advisor", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS / Styling ----------
st.markdown("""
<style>
:root {
  --primary: #4F46E5;
  --muted: #6B7280;
  --card-bg: #FFFFFF;
  --page-bg: #F8FAFC;
}
body { background-color: var(--page-bg); }
.app-title { font-size:34px; font-weight:800; color:var(--primary); text-align:center; margin-bottom:4px; }
.app-sub { text-align:center; color:var(--muted); margin-bottom:18px; }
.role-card { border-radius:14px; padding:16px; background:var(--card-bg); box-shadow: 0 6px 20px rgba(15,23,42,0.06); }
.small { font-size:13px; color:var(--muted); }
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
        "experience": 1, "career_goal": "Data Scientist", "interests": ["AI","Data"], "skills": ["python","sql","statistics"]
    },
    "Bob (AI Engineer)": {
        "name": "Bob", "age": 28, "gender": "Male", "education": "Postgraduate",
        "experience": 4, "career_goal": "AI Engineer", "interests": ["Deep Learning","NLP"], "skills": ["python","deep learning","tensorflow"]
    },
    "Charlie (Career Switcher)": {
        "name": "Charlie", "age": 35, "gender": "Male", "education": "Postgraduate",
        "experience": 10, "career_goal": "Product Manager", "interests": ["Business","AI"], "skills": ["communication","excel","strategy"]
    }
}

if sample_choice != "None":
    st.sidebar.success(f"Loaded sample: {sample_choice}")
    st.session_state["profile"] = SAMPLES[sample_choice]

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit • Local mock AI by default")

# ---------- Top header ----------
st.markdown("<div class='app-title'>🎯 AI Career & Skills Advisor</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub'>Map your skills → roles → step-by-step roadmap</div>", unsafe_allow_html=True)
st.divider()

# ---------- Profile form ----------
# Use session_state profile if loaded from sample, otherwise show form
if "profile" in st.session_state:
    # Show summary and allow edit if user wants
    with st.expander("👤 Edit loaded profile", expanded=False):
        profile = collect_user_profile(prefill=st.session_state.get("profile"))
else:
    profile = collect_user_profile()

# Skills input (single-line, comma separated)
skills_input = st.text_input("Your Skills (comma separated)", placeholder="Python, SQL, Machine Learning", value=", ".join(profile.get("skills", [])))
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
                with cols[i]:
                    show_career_card(m["role"], m["match"], m["about"], m.get("missing", []))

                    # Learning plan expander (mock by default)
                    with st.expander(f"📚 View Learning Plan — {m['role']}", expanded=False):
                        if enable_gemini:
                            # call real planner once (optional)
                            plan = generate_learning_plan(profile.get("skills", []), m["role"])
                            st.write(plan)
                        else:
                            mock_plan = [f"Week {w+1}: Study {topic}" for w, topic in enumerate((m.get("missing") or ["python", "sql"]))][:12]
                            st.write("\n".join([f"{i+1}. {step}" for i, step in enumerate(mock_plan)]))

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
