import streamlit as st

def show_career_card(title, match_score, description, missing_skills):
    st.markdown(f"""
    <div class='role-card'>
        <div style='font-size:18px; font-weight:700; color:#111827;'>{title}
            <span style='float:right; background:#E0E7FF; color:#3730A3; padding:6px 10px; border-radius:12px; font-weight:700;'>{match_score}%</span>
        </div>
        <div style='color:#6B7280; margin-top:8px;'>{description}</div>
        <div style='margin-top:10px;'>
            <span style='display:inline-block; padding:6px 10px; border-radius:12px; background:#F1F5F9; font-size:12px;'>Missing: {", ".join(missing_skills) if missing_skills else "None 🎉"}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
