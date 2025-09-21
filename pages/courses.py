import streamlit as st

# This acts as a local, offline database for learning resources.
RESOURCES = {
    "AI Engineer": {
        "foundational": {
            "summary": "Your score indicates a good opportunity to strengthen your core fundamentals. This plan focuses on building a rock-solid base in machine learning theory and practical Python skills before diving into advanced topics.",
            "plan": [
                "**Week 1-2: Python & Data Science Libraries.** Master NumPy, Pandas, and Matplotlib.",
                "**Week 3-4: Core Machine Learning Concepts.** Deeply understand supervised vs. unsupervised learning, regression, classification, and model evaluation metrics.",
                "**Week 5-6: Introduction to Deep Learning.** Learn the basics of neural networks, activation functions, and backpropagation.",
                "**Week 7-8: MLOps Fundamentals.** Understand the basics of deploying and monitoring models."
            ],
            "courses": [
                {"title": "Machine Learning Specialization", "provider": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
                {"title": "Python for Data Science and Machine Learning Bootcamp", "provider": "Udemy", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"},
                {"title": "Deep Learning Fundamentals", "provider": "Cognitive Class.ai", "url": "https://cognitiveclass.ai/courses/deep-learning-fundamentals"}
            ],
            "websites": [
                {"name": "Kaggle Learn Courses", "url": "https://www.kaggle.com/learn"},
                {"name": "Towards Data Science", "url": "https://towardsdatascience.com/"},
                {"name": "Machine Learning Mastery", "url": "https://machinelearningmastery.com/"}
            ],
            "youtube": [
                {"channel": "StatQuest with Josh Starmer", "url": "https://www.youtube.com/c/statquest"},
                {"channel": "3Blue1Brown (Neural Networks Series)", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_5LHyA2GvwaLR6wP_"},
                {"channel": "Krish Naik", "url": "https://www.youtube.com/user/krishnaik06"}
            ]
        },
        "advanced": {
            "summary": "You have a strong foundation! This plan is designed to push you into more specialized, high-demand areas of AI Engineering, focusing on production-level skills and cutting-edge topics.",
             "plan": [
                "**Week 1-2: Advanced Deep Learning Architectures.** Explore Transformers, GANs, and Attention mechanisms.",
                "**Week 3-4: MLOps in Practice.** Implement a full CI/CD pipeline for a machine learning model using Docker, Kubernetes, and a tool like Kubeflow or MLflow.",
                "**Week 5-6: Large Language Models (LLMs).** Fine-tune a pre-trained LLM (e.g., GPT-2, T5) on a custom dataset.",
                "**Week 7-8: Scalable Data Processing.** Work with distributed computing frameworks like Spark or Dask for large-scale feature engineering."
            ],
            "courses": [
                {"title": "DeepLearning.AI TensorFlow Developer Professional Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"},
                {"title": "Full Stack Machine Learning", "provider": "The Full Stack", "url": "https://fullstackdeeplearning.com/course/2022/"},
                {"title": "Machine Learning Engineering for Production (MLOps) Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"}
            ],
             "websites": [
                {"name": "Papers with Code", "url": "https://paperswithcode.com/"},
                {"name": "Hugging Face (Models & Courses)", "url": "https://huggingface.co/"},
                {"name": "Distill.pub", "url": "https://distill.pub/"}
            ],
            "youtube": [
                {"channel": "Yannic Kilcher", "url": "https://www.youtube.com/c/YannicKilcher"},
                {"channel": "Abhishek Thakur", "url": "https://www.youtube.com/c/AbhishekThakurAbhi"},
                {"channel": "Lex Fridman", "url": "https://www.youtube.com/c/lexfridman"}
            ]
        }
    },
    # You can add more roles here following the same structure
    "Data Scientist": {
        # ... add foundational and advanced plans for Data Scientist
    }
}


# --- Page Title ---
st.markdown("<div class='app-title'>📚 Career Learning Plans</div>", unsafe_allow_html=True)


# --- New Logic: Role Selection ---
# Use the role from the interview if available, otherwise let the user choose.
role_options = list(RESOURCES.keys())
pre_selected_index = 0
if 'chosen_career' in st.session_state and st.session_state.chosen_career in role_options:
    pre_selected_index = role_options.index(st.session_state.chosen_career)

selected_role = st.selectbox(
    "Select a Career Role to see the learning plan:",
    options=role_options,
    index=pre_selected_index
)


# --- New Logic: Determine Plan & Show Message ---
plan_type = "foundational"  # Default to foundational plan
message_container = st.container() # To show the right message

# Check if a score exists to show a personalized plan
if 'final_score' in st.session_state and 'chosen_career' in st.session_state and selected_role == st.session_state.chosen_career:
    score = st.session_state.final_score
    plan_type = "advanced" if score >= 70 else "foundational"
    message_container.success(f"This is a **{plan_type}** plan, personalized based on your {score:.1f}% interview score for the **{selected_role}** role.")
else:
    message_container.info("This is a general learning plan. For a plan personalized to your skills, complete an interview on the main page!")


# --- Display the selected plan ---
if selected_role in RESOURCES and plan_type in RESOURCES[selected_role]:
    data = RESOURCES[selected_role][plan_type]

    st.header(f"🗓️ 8-Week Learning Roadmap for {selected_role}")
    with st.container(border=True):
        for item in data["plan"]:
            st.markdown(f"- {item}")
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.header("🎓 Top Course Recommendations")
        for course in data["courses"]:
            st.markdown(f"**[{course['title']}]({course['url']})** on _{course['provider']}_")

        st.header("🌐 Helpful Websites")
        for site in data["websites"]:
            st.markdown(f"- [{site['name']}]({site['url']})")

    with col2:
        st.header("📺 Recommended YouTube Channels")
        for yt in data["youtube"]:
            st.markdown(f"- [{yt['channel']}]({yt['url']})")
else:
    st.error(f"Sorry, we don't have a learning plan for '{selected_role}' yet.")

st.divider()
if st.button("⬅️ Back to Career Advisor"):
    st.switch_page("streamlit_app.py")