# ui_components.py
import streamlit as st

def show_career_card(title, match_score, description, missing_skills):
    st.markdown(f"""
    <div class='role-card'>
        <div style='font-size:20px; font-weight:600;'>{title}
            <span class='match-badge'>{match_score}% match</span>
        </div>
        <div style='color:#555; margin-top:6px;'>{description}</div>
        <div style='margin-top:10px;'>
            <span class='tag'>Missing: {', '.join(missing_skills) if missing_skills else 'None 🎉'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
