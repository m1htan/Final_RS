from pathlib import Path

import streamlit as st


def apply_custom_style() -> None:
    """Inject CSS from the bundled stylesheet if it exists."""

    style_path = Path(__file__).resolve().parent / "app_style.css"
    if not style_path.exists():
        return

    css = style_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
