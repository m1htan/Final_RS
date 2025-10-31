import streamlit as st

def apply_custom_style():
    """Inject CSS from external stylesheet."""
    with open("/Users/minhtan/Documents/GitHub/RecommendationSystem/final/src/style/app_style.css") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
