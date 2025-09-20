import streamlit as st

from engine.advisor import get_personalized_advice  # Assuming we can reuse or adapt for evaluation

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Mock Interview",
    page_icon="🎤",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
custom_css = """<style>
/* Background */
.stApp {background: linear-gradient(135deg, #eef2ff 0%, #fef9f9 100%); color: #000000 !important;}
.main-card {background:#fff;border-radius:18px;padding:2rem;margin:auto;width:65%;
box-shadow:0px 8px 28px rgba(0,0,0,0.08);text-align:center; color: #000000 !important;}
.role-heading {font-size:20px;font-weight:600;color:#1e3a8a;margin-bottom:1rem;}
.q-label {font-size:14px;font-weight:600;color:#6a5acd;margin-bottom:0.5rem;
text-transform:uppercase;letter-spacing:1px;}
.q-text {font-size:22px;font-weight:600;color:#111;margin-bottom:1.5rem;line-height:1.4;}
.q-progress {font-size:14px;color:#666;text-align:right;margin-top:-15px;}
.radio-wrapper {display:flex;justify-content:center;margin-top:20px;}
.radio-wrapper > div {text-align:left;}
div.stRadio label {font-size:18px !important;font-weight:500 !important;color:#222 !important;cursor:pointer;}
div.stRadio label:hover {color:#2563eb !important;}
div.stButton > button {border-radius:12px;font-size:18px;padding:0.7rem 1.4rem;
border:2px solid #2563eb;background-color:white;color:#2563eb;font-weight:600;
transition:all 0.25s ease;margin-top:20px;}
div.stButton > button:hover {background-color:#2563eb;color:white;transform:scale(1.04);}
.feedback {margin-top:20px; padding:10px; border:1px solid #ccc; border-radius:8px; color: #000000 !important;}
.scorecard {margin-top:30px; padding:20px; background:#ffffff; border-radius:12px; color: #000000 !important; border: 1px solid #e0e0e0;}
.scorecard h3 {color: #000000 !important;}
.scorecard p {color: #000000 !important; font-weight: 500;}
.stMarkdown, .stText, .stCaption, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError { color: #000000 !important; }
</style>"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Settings")
enable_gemini = st.sidebar.checkbox("🔑 Enable Gemini for Evaluation", value=False)

# ---------- ROLE ----------
role = st.session_state.get("chosen_career", "Data Scientist")  # from career card

# ---------- QUESTION BANK ----------
QUESTIONS = {
    "Data Scientist": [
        "Explain the Difference Between Classification and Regression?",
        "What is Bias in Machine Learning?",
        "What is Cross-Validation?",
        "What are Support Vectors in SVM?",
        "Explain SVM Algorithm in Detail",
        "What is PCA? When do you use it?",
        "What is ‘Naive’ in a Naive Bayes?",
        "What is Unsupervised Learning?",
        "What is Supervised Learning?",
        "What are Different Types of Machine Learning algorithms?",
        "What is F1 score? How would you use it?",
        "Define Precision and Recall?",
        "How to Tackle Overfitting and Underfitting?",
        "What is a Neural Network?",
        "What are Loss Function and Cost Functions? Explain the key Difference Between them?"
    ],
    "Backend Developer": [
        "What is the difference between ArrayList and LinkedList in Java?",
        "Explain the concept of multithreading in Java.",
        "State difference between GraphQL and REST.",
        "What is CI (Continuous Integration)?",
        "Explain event loop in Node.js.",
        "Is there a way to decrease the load time of a web application?",
        "Explain dependency injection.",
        "State difference between normalization and denormalization.",
        "What is Promise and explain its states?",
        "State the difference between GET and POST.",
        "Explain the Restful API and write its usage.",
        "What do you mean by MEAN Stack?",
        "What makes MVC different from MVP?",
        "Explain inversion of control.",
        "What do you mean by CORS (Cross-Origin Resource Sharing)?"
    ],
    "Frontend Developer": [
        "What is the difference between margin and padding in CSS?",
        "Explain how flexbox works in CSS.",
        "What is the event loop in JavaScript?",
        "Explain the difference between let, const, and var in JavaScript.",
        "What is a closure in JavaScript?",
        "Explain responsive design and how to implement it.",
        "What is the DOM and how do you manipulate it?",
        "What is the difference between == and === in JavaScript?",
        "Explain event bubbling and capturing in JavaScript.",
        "What is a promise in JavaScript?",
        "How does HTTP work?",
        "What is CORS and how to handle it?",
        "Explain the box model in CSS.",
        "What is a service worker?",
        "How to optimize website performance?"
    ],
    "Full Stack Developer": [
        "Explain the meaning of multithreading.",
        "Which language is the most preferred by full-stack developers?",
        "Explain Pair Programming.",
        "What do you mean by CORS (Cross-Origin Resource Sharing)?",
        "What is Callback Hell?",
        "Explain Long Polling.",
        "Can you tell me what are the latest trends in Full Stack Development? Also, how do you keep yourself updated about the new trends in the industry?",
        "State difference between GraphQL and REST (Representational State Transfer).",
        "What is CI (Continuous Integration)?",
        "To develop a project from scratch, what technologies and languages would you need or what skills a full stack developer should have?",
        "Explain the benefits and drawbacks of using 'use strict'.",
        "What are some of the uses of Docker?",
        "Explain event loop in Node.js.",
        "Is there a way to decrease the load time of a web application?",
        "Explain dependency injection."
    ],
    "AI Engineer": [
        "What are the main types of AI?",
        "How does machine learning differ from traditional programming?",
        "What is a Neural Network?",
        "What are Loss Function and Cost Functions? Explain the key Difference Between them?",
        "What is Ensemble learning?",
        "How do you make sure which Machine Learning Algorithm to use?",
        "How to Handle Outlier Values?",
        "What is a Random Forest? How does it work?",
        "What is Collaborative Filtering? And Content-Based Filtering?",
        "What is Clustering?",
        "How can you select K for K-means Clustering?",
        "What are Recommender Systems?",
        "Can logistic regression use for more than 2 classes?",
        "Explain Correlation and Covariance?",
        "What is P-value?"
    ],
    "Machine Learning Engineer": [
        "Explain the Difference Between Classification and Regression?",
        "What is Bias in Machine Learning?",
        "What is Cross-Validation?",
        "Explain SVM Algorithm in Detail",
        "What is PCA? When do you use it?",
        "What is Unsupervised Learning?",
        "What is Supervised Learning?",
        "What is F1 score? How would you use it?",
        "Define Precision and Recall?",
        "How to Tackle Overfitting and Underfitting?",
        "What are Loss Function and Cost Functions? Explain the key Difference Between them?",
        "What is Ensemble learning?",
        "How do you make sure which Machine Learning Algorithm to use?",
        "What is a Random Forest? How does it work?",
        "What is Clustering?"
    ],
    "DevOps Engineer": [
        "What is configuration management?",
        "What is the importance of having configuration management in DevOps?",
        "What is Continuous Integration (CI)?",
        "Why is Continuous Integration needed?",
        "What is Continuous Testing (CT)?",
        "What can be a preparatory approach for developing a project using the DevOps methodology?",
        "How does AWS contribute to DevOps?",
        "How does Ansible work?",
        "Can you say something about the DevOps pipeline?",
        "Can you differentiate between continuous testing and automation testing?",
        "Explain the different phases in DevOps methodology.",
        "How is DevOps different than the Agile Methodology?",
        "Can you explain the “Shift left to reduce failure” concept in DevOps?",
        "Can you explain the “infrastructure as code” (IaC) concept?",
        "What is Blue/Green Deployment Pattern?"
    ],
    "Cloud Architect": [
        "What is a Cloud Technology?",
        "Describe the Cloud Computing Architecture.",
        "What are the different versions of the cloud?",
        "What do you mean by cloud delivery models?",
        "What are some of the key features of Cloud Computing?",
        "How does Resource Replication take place in Cloud Computing?",
        "What are some issues with Cloud Computing?",
        "What are Low-Density Data Centers?",
        "What are Containerized Data Centers?",
        "What do you mean by encapsulation in cloud computing?",
        "What is meant by Edge Computing?",
        "What are Cloud-Native Applications?",
        "Why are microservices important for a true cloud environment?",
        "What are Microservices?",
        "What are the advantages and disadvantages of serverless computing?"
    ],
    "Cybersecurity Analyst": [
        "What do you mean by a Null Session?",
        "Differentiate between threat, vulnerability, and risk.",
        "What does XSS stand for? How can it be prevented?",
        "What is a Firewall?",
        "Define VPN.",
        "Who are Black Hat, White Hat, and Grey Hat Hackers?",
        "What are the types of Cyber Security?",
        "What do you mean by a botnet?",
        "What do you mean by honeypots?",
        "Differentiate between Vulnerability Assessment and Penetration Testing.",
        "What is the main objective of Cyber Security?",
        "What do you mean by brute force in the context of Cyber Security?",
        "What do you mean by Shoulder Surfing?",
        "What do you mean by Phishing?",
        "Differentiate between hashing and encryption."
    ],
    "Blockchain Developer": [
        "What is Blockchain?",
        "What are the different types of Blockchain?",
        "What is a smart contract?",
        "Explain consensus algorithms in Blockchain.",
        "What is Proof of Work?",
        "What is Proof of Stake?",
        "What is a Merkle Tree?",
        "Explain cryptography in Blockchain.",
        "What is a wallet in Blockchain?",
        "What are the challenges in Blockchain implementation?",
        "Explain DApps.",
        "What is Solidity?",
        "Explain gas in Ethereum.",
        "What is a nonce?",
        "Explain mining in Blockchain."
    ],
    "Data Engineer": [
        "What is Apache Spark?",
        "What is the difference between Spark and MapReduce?",
        "What is Data Modeling?",
        "What is the difference between a data engineer and a data scientist?",
        "What are the features of Hadoop?",
        "Explain MapReduce in Hadoop.",
        "What is Data Engineering?",
        "Explain the Star Schema in Brief.",
        "Explain the Snowflake Schema in Brief.",
        "What was the algorithm you used in a recent project?",
        "What do you mean by data pipeline?",
        "What is orchestration?",
        "What are different data validation approaches?",
        "Why are you applying for the Data Engineer role in our company?",
        "What challenges did you face in your recent project"
    ],
    "Mobile App Developer": [
        "What are the features of Android architecture?",
        "List the languages used to build Android.",
        "What is a service in Android?",
        "Differentiate Activities from Services.",
        "What is Google Android SDK? Which are the tools placed in Android SDK?",
        "What is the use of Bundle in Android?",
        "What is an Adapter in Android?",
        "Explain the difference between Implicit and Explicit Intent.",
        "What is ANR in Android? What are the measures you can take to avoid ANR?",
        "Explain different launch modes in Android.",
        "What is the life cycle of Android activity?",
        "Explain Sensors in Android.",
        "Explain the dialog boxes supported on Android.",
        "What is AndroidManifest.xml file and why do you need this?",
        "What is the difference between Serializable and Parcelable? Which is the best approach in Android?"
    ],
    "Game Developer": [
        "What is the difference between 2D and 3D game development?",
        "Explain the game loop.",
        "What is a sprite?",
        "What is collision detection and how is it implemented?",
        "What is level design?",
        "Explain AI in games.",
        "What is pathfinding?",
        "What are shaders?",
        "How to optimize game performance?",
        "What is Unity and what are its main features?",
        "What is Unreal Engine?",
        "Explain physics in games.",
        "What is animation in games?",
        "What is multiplayer game development challenges?",
        "How to handle input in games?"
    ],
    "Product Manager": [
        "What is your favorite product and how would you improve it?",
        "How do you prioritize features?",
        "What is the difference between a product manager and a project manager?",
        "How do you define success for a product?",
        "Describe your process for launching a new product.",
        "How do you gather and prioritize customer feedback?",
        "What metrics do you track for product performance?",
        "How do you handle competing priorities from different stakeholders?",
        "What is a MVP and why is it important?",
        "Explain the product lifecycle.",
        "How do you conduct market research?",
        "What is A/B testing and how do you use it?",
        "How do you work with engineering teams?",
        "What is your experience with agile methodologies?",
        "Tell me about a product failure and what you learned."
    ],
    "UI/UX Designer": [
        "What is the difference between UI and UX?",
        "Describe your design process.",
        "What tools do you use for prototyping?",
        "How do you conduct user research?",
        "What is wireframing?",
        "Explain user personas.",
        "What is usability testing?",
        "How do you ensure accessibility in designs?",
        "What is responsive design?",
        "Explain information architecture.",
        "What is A/B testing in UX?",
        "How do you handle feedback?",
        "What is the role of color theory in design?",
        "Explain microinteractions.",
        "How do you stay updated with trends?"
    ],
    "Digital Marketing Specialist": [
        "What is digital marketing?",
        "Explain SEO.",
        "What is PPC?",
        "What is content marketing?",
        "Explain social media marketing.",
        "What is email marketing?",
        "How do you measure ROI?",
        "What is a conversion rate?",
        "Explain A/B testing.",
        "What is Google Analytics?",
        "How do you stay updated with trends?",
        "What is influencer marketing?",
        "Explain inbound marketing.",
        "What is the difference between organic and paid search?",
        "How do you handle a crisis in social media?"
    ]
}

# ---------- STATE INIT ----------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.answers = []
    st.session_state.feedbacks = []
    st.session_state.scores = []  # List of dicts: {'correctness': x, 'communication': y, 'relevance': z}

if "difficulty" not in st.session_state:
    difficulty_options = ["Easy (5 questions)", "Medium (10 questions)", "Hard (15 questions)"]
    selected_diff = st.selectbox("Select Difficulty", difficulty_options)
    if selected_diff == "Easy (5 questions)":
        st.session_state.num_questions = 5
    elif selected_diff == "Medium (10 questions)":
        st.session_state.num_questions = 10
    else:
        st.session_state.num_questions = 15
    st.session_state.difficulty = selected_diff

# Get questions for the role
if role in QUESTIONS:
    questions = QUESTIONS[role][:st.session_state.num_questions]
else:
    questions = QUESTIONS["Data Scientist"][:st.session_state.num_questions]  # Fallback

# ---------- EVALUATION FUNCTION ----------
def evaluate_answer(question, answer, use_mock=True):
    if use_mock:
        # Dummy evaluation
        correctness = 8
        communication = 7
        relevance = 9
        feedback = "Good answer. Could be more detailed."
    else:
        # Real Gemini call (adapt from advisor.py)
        try:
            prompt = f"Evaluate the following answer to the question '{question}':\n\n{answer}\n\nProvide scores out of 10 for: Correctness, Communication, Relevance. Then, give brief feedback."
            # Assuming similar to get_personalized_advice
            advice = get_personalized_advice({}, [], use_mock=False)  # Placeholder, adapt prompt
            # Parse response (assuming format: Correctness: x\nCommunication: y\nRelevance: z\nFeedback: ...)
            lines = advice.splitlines()
            correctness = int(lines[0].split(': ')[1])
            communication = int(lines[1].split(': ')[1])
            relevance = int(lines[2].split(': ')[1])
            feedback = '\n'.join(lines[3:])
        except:
            correctness, communication, relevance = 5, 5, 5
            feedback = "Error in evaluation. Using default scores."
    
    return {
        'correctness': correctness,
        'communication': communication,
        'relevance': relevance
    }, feedback

# ---------- CURRENT QUESTION ----------
if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]

    st.markdown(f"<p class='role-heading'>Mock Interview — {role}</p>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="main-card">
            <p class="q-label">Question {st.session_state.q_index+1}</p>
            <p class="q-text">{q}</p>
            <p class="q-progress">{st.session_state.q_index+1} / {len(questions)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_answer = st.text_area("Your Answer:", key=f"q_{st.session_state.q_index}")

    if st.button("Submit Answer ➡️"):
        if user_answer:
            with st.spinner("Evaluating..."):
                scores, feedback = evaluate_answer(q, user_answer, enable_gemini)
                st.session_state.answers.append(user_answer)
                st.session_state.feedbacks.append(feedback)
                st.session_state.scores.append(scores)
                st.session_state.q_index += 1
                st.rerun()
        else:
            st.warning("⚠️ Please provide an answer before submitting.")
else:
    # ---------- RESULTS ----------
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

        # Feedback & Next Steps
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
                    st.write("- Recommended: Online courses on Coursera or edX for role-specific skills.")
                elif area == "Communication skills":
                    st.write("- Recommended: Practice mock interviews or join Toastmasters.")
                else:
                    st.write("- Recommended: Read books like 'Cracking the PM Interview' or solve case studies.")
        else:
            st.write("Strong performance across all areas! Suggested job roles: Senior positions or specializations in your field.")

        st.balloons()

    if st.button("🔄 Retry Interview"):
        st.session_state.q_index = 0
        st.session_state.answers = []
        st.session_state.feedbacks = []
        st.session_state.scores = []
        del st.session_state.difficulty
        st.rerun()

    if st.button("⬅️ Back to Career Advisor"):
        st.switch_page("streamlit.py")  # Assuming the main page is streamlit.py