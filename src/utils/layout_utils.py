import streamlit as st
import pandas as pd

def show_profile_card(user):
    cols = st.columns([1, 2])
    with cols[0]:
        #st.image(f"/Users/minhtan/Documents/GitHub/RecommendationSystem/final/images/{user.get('user_id', '')}.jpg", width=120)
        st.image("/Users/minhtan/Documents/GitHub/RecommendationSystem/final/images/U0001.jpg", width=120)
    with cols[1]:
        st.subheader(f"{user.get('first_name', '')} {user.get('last_name', '')}")
        st.write(f"**Gender:** {user.get('gender', '-')}")
        st.write(f"**City:** {user.get('city', '-')}")
        st.write(f"**Major:** {user.get('major', '-')}")
        st.write(f"**Degree:** {user.get('degree_type', '-')}")
        st.write(f"**GPA:** {user.get('gpa', '-')}")
        st.write(f"**Skills:** {user.get('skill_name', [])}")

def show_job_cards(jobs_df: pd.DataFrame):
    for _, row in jobs_df.iterrows():
        with st.container():
            st.markdown(f"#### Job ID: `{row['jid']}`")
            st.write(f"**Required Skills:** {row['proj_quals']}")
            st.divider()

def show_course_cards(recs_df: pd.DataFrame):
    for _, c in recs_df.iterrows():
        st.markdown(f"#### {c['course_name']}")
        st.write(f"**Skills Taught:** {c['skills_taught']}")
        st.write(f"**Provider:** {c['provider']}")
        st.write(f"**Rating:** {c['rating']}")
        st.write(f"**Duration:** {c['duration_hours']} hours")
        st.progress(float(c['score']))
        st.divider()
