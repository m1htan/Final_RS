import streamlit as st
from utils.recommender import load_model, get_user_info, top_jobs_for_user, recommend_for_user
from utils.layout_utils import (
    show_course_cards,
    show_job_cards,
    show_job_detail,
    show_profile_card,
)
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

if "job_detail_mode" not in st.session_state:
    st.session_state.job_detail_mode = False

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None

if "job_click_nonce" not in st.session_state:
    st.session_state.job_click_nonce = None

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
            st.session_state.job_detail_mode = False
            st.session_state.selected_job_id = None
            st.session_state.job_click_nonce = None
            st.success(f"Welcome back, {user_id}! Redirecting...")
            st.rerun()
        else:
            st.error("We couldn't find that ID. Please check and try again.")
    st.stop()

col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.job_detail_mode = False
        st.session_state.selected_job_id = None
        st.session_state.job_click_nonce = None
        st.rerun()

user_id = st.session_state.user_id
st.markdown(f"### Hello, {user_id}!")
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
    st.markdown(
        """
        <section class="job-match-hero" id="job-match">
            <div class="job-hero-copy">
                <h2>Find Job</h2>
                <p>Discover curated opportunities that align with your strengths and aspirations.</p>
            </div>
            <div class="job-filter-bar">
                <div class="filter-field wide">
                    <label>Search</label>
                    <div class="input-shell">
                        <span class="input-icon"></span>
                        <input type="text" placeholder="Search job title or keyword" />
                    </div>
                </div>
                <div class="filter-field">
                    <label>Location</label>
                    <div class="input-shell">
                        <select>
                            <option selected>All locations</option>
                            <option>Remote</option>
                            <option>On-site</option>
                        </select>
                    </div>
                </div>
                <div class="filter-field">
                    <label>Job type</label>
                    <div class="input-shell">
                        <select>
                            <option selected>Any type</option>
                            <option>Full-time</option>
                            <option>Part-time</option>
                            <option>Contract</option>
                        </select>
                    </div>
                </div>
                <div class="filter-field">
                    <label>Salary range</label>
                    <div class="input-shell">
                        <select>
                            <option selected>All ranges</option>
                            <option>Up to $60k</option>
                            <option>$60k - $90k</option>
                            <option>$90k - $120k</option>
                            <option>$120k+</option>
                        </select>
                    </div>
                </div>
                <button type="button" class="filter-button">Search</button>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    jobs = top_jobs_for_user(data, user_id, n=6)
    if jobs is not None and not jobs.empty:
        if st.session_state.get("job_detail_mode") and not st.session_state.get("selected_job_id"):
            st.session_state.job_detail_mode = False

        job_detail_mode = st.session_state.get("job_detail_mode", False)
        if not job_detail_mode:
            st.markdown(
                f"""
                <div class="job-results-header">
                    <div>
                        <h3>Job match</h3>
                        <p>Based on your profile data</p>
                    </div>
                    <span class="results-count">{len(jobs)} roles available</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            show_job_cards(jobs)
            if st.session_state.get("job_detail_mode", False):
                st.rerun()
        else:
            selected_job_id = st.session_state.get("selected_job_id")
            selected_row = None
            resolved_id = str(selected_job_id) if selected_job_id is not None else None
            if resolved_id:
                for key in ("jid", "job_id", "id"):
                    if key in jobs.columns:
                        matches = jobs[jobs[key].astype(str) == resolved_id]
                        if not matches.empty:
                            selected_row = matches.iloc[0]
                            break
            if selected_row is None and not jobs.empty:
                selected_row = jobs.iloc[0]
                fallback_id = (
                    selected_row.get("jid")
                    or selected_row.get("job_id")
                    or selected_row.get("id")
                    or 0
                )
                st.session_state["selected_job_id"] = str(fallback_id)

            back_col, _ = st.columns([0.2, 0.8])
            with back_col:
                if st.button("← Back to job list", use_container_width=True):
                    st.session_state["job_detail_mode"] = False
                    st.session_state["selected_job_id"] = None
                    st.rerun()

            show_job_detail(selected_row)
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