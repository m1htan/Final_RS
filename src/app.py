import streamlit as st
from utils.recommender import load_model, get_user_info, top_jobs_for_user, recommend_for_user
from utils.layout_utils import show_profile_card, show_job_cards, show_course_cards
from style.layout_style import apply_custom_style

st.set_page_config(page_title="SkillGraph System", layout="wide")

# Apply global style
apply_custom_style()

st.title("SkillGraph Recommender System")
st.caption("Discover tailored job matches and courses designed around your strengths.")

@st.cache_resource
def init_model():
    return load_model()

data = init_model()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.user_id:
    st.markdown("<h3 class='centered-text'>Login to your account</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="empty-state">Enter your employee ID to see personalised insights.</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.25, 0.5, 0.25])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            user_id = st.text_input("User ID", placeholder="e.g. U0001", max_chars=20)
            submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if user_id and user_id in data["employee_df"]["user_id"].values:
            st.session_state.user_id = user_id
            st.success(f"Welcome back, {user_id}! Redirecting...")
            st.rerun()
        else:
            st.error("We couldn't find that ID. Please check and try again.")
    st.stop()

col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

user_id = st.session_state.user_id
st.markdown(f"### 👋 Hello, {user_id}!")
st.info("Explore the tabs below to review your profile, discover matching roles, and close any skill gaps with curated courses.")

tabs = st.tabs(["Profile", "Job Match", "Learning Path"])

with tabs[0]:
    st.subheader("Your Profile")
    user = get_user_info(data, user_id)
    if user is not None:
        show_profile_card(user)
    else:
        st.warning("User not found in dataset.")

with tabs[1]:
    st.subheader("Top Matching Jobs")
    st.markdown("<div id='job-match'></div>", unsafe_allow_html=True)
    jobs = top_jobs_for_user(data, user_id, n=5)
    if jobs is not None and not jobs.empty:
        show_job_cards(jobs)
    else:
        st.info("No job match data available for this user.")

with tabs[2]:
    st.subheader("Recommended Courses to Close Skill Gap")
    st.markdown("<div id='learning-path'></div>", unsafe_allow_html=True)
    recs = recommend_for_user(data, user_id)
    if recs is not None and not recs.empty:
        show_course_cards(recs)
    else:
        st.info("No learning recommendations available yet.")