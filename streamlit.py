import streamlit as st

from user_profile import collect_user_profile
from engine.matcher import match_careers
from engine.planner import generate_learning_plan
from engine.advisor import get_personalized_advice

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Career Advisor", page_icon="🎓", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
    body { background-color: #F8FAFC; }
    .title { font-size: 40px; font-weight: 800; text-align:center; color:#4F46E5; }
    .subtitle { text-align:center; font-size: 18px; color: #555; margin-bottom: 12px; }
    .role-card {
        background: #F9FAFB; padding: 20px; border-radius: 16px;
        margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .role-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        transition: 0.2s ease;
    }
    .match-badge {
        background: #E0E7FF; color: #3730A3;
        padding: 4px 10px; border-radius: 12px; font-size: 13px;
        float:right;
    }
    .tag {
        display:inline-block; padding:5px 10px; border-radius:12px;
        background:#F1F5F9; margin:4px; font-size:12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.markdown("<div class='title'>🎯 AI Career & Skills Advisor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Map your skills → roles → roadmap</div>", unsafe_allow_html=True)
st.divider()

# ---------- Collect User Profile ----------
user_profile = collect_user_profile()

# ---------- Skills Input ----------
skills_input = st.text_input(
    "Your Skills (comma separated)",
    placeholder="Python, SQL, Machine Learning"
)

# ---------- Analyze Button ----------
if st.button("🚀 Analyze My Career Path"):
    if not skills_input.strip():
        st.warning("Please enter your skills first.")
    else:
        # Merge skills into profile
        user_skills = [s.strip().lower() for s in skills_input.split(",") if s.strip()]
        user_profile["skills"] = user_skills

        # ---------- Career Matching ----------
        matches = match_careers(user_skills)
        st.subheader("📌 Top 3 Career Matches")
        for m in matches[:3]:
            st.markdown(f"""
            <div class='role-card'>
                <div style='font-size:20px; font-weight:600; color:#4F46E5;'>{m['role']}
                    <span class='match-badge'>{m['match']}% match</span>
                </div>
                <div style='color:#555; margin-top:6px;'>{m['about']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(m['match'] / 100.0)
            if m.get('missing'):
                st.markdown("**Missing Skills:** " + ", ".join([f"`{s}`" for s in m['missing']]))

             # ---------- Learning Plan Section ----------(Only use for now to avoid Gemini API calls)
             
            with st.expander(f"📚 View Learning Plan for {m['role']}", expanded=False):
                # Use mock learning plan for now
                mock_plan = [
                    f"Learn {s.capitalize()} fundamentals" for s in (m.get('missing') or ['Python', 'SQL'])
                ]
                mock_plan.append(f"Work on a project relevant to {m['role']}")
                mock_plan.append("Build portfolio and practice interview questions")

                st.write("\n".join([f"{i+1}. {step}" for i, step in enumerate(mock_plan)]))

        # ---------- Personalized Advice (Mock) ----------
        st.subheader("✨ Personalized AI Career Guidance")
        with st.spinner("Thinking with Gemini... 🤖"):
            advice = get_personalized_advice(user_profile, matches[:3], use_mock=True)
        st.write(advice or "No advice generated.")
