import streamlit as st
from utils.recommender import load_model, get_user_info, top_jobs_for_user, recommend_for_user
from utils.layout_utils import show_profile_card, show_job_cards, show_course_cards
from style.layout_style import apply_custom_style

st.set_page_config(page_title="SkillGraph System", layout="wide")

# Apply global style
apply_custom_style()

st.title("SkillGraph Recommender System")

@st.cache_resource
def init_model():
    return load_model()

data = init_model()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.user_id:
    st.markdown("<h3 class='centered-text'>Login to your account</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    with col2:
        user_id = st.text_input("User ID", placeholder="e.g. U0001")
        login_button = st.button("Login")

    if login_button:
        if user_id and user_id in data["employee_df"]["user_id"].values:
            st.session_state.user_id = user_id
            st.success(f"Welcome, {user_id}")
            st.rerun()
        else:
            st.error("User ID not found. Please check again.")
    st.stop()

col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

user_id = st.session_state.user_id
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
    jobs = top_jobs_for_user(data, user_id, n=5)
    if jobs is not None and not jobs.empty:
        show_job_cards(jobs)
    else:
        st.info("No job match data available for this user.")

with tabs[2]:
    st.subheader("Recommended Courses to Close Skill Gap")
    recs = recommend_for_user(data, user_id)
    if recs is not None and not recs.empty:
        show_course_cards(recs)
    else:
        st.info("No learning recommendations available yet.")