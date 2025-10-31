import base64
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = REPO_ROOT / "images"


def _render_tags(items: Iterable[str]) -> str:
    tags = [f"<span class='pill'>{item.strip()}</span>" for item in items if item and item.strip()]
    return "".join(tags)


def _safe_split(value: str) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [piece.strip() for piece in str(value).split(",") if piece.strip()]


def _image_as_data_uri(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{path.suffix.lstrip('.')};base64,{encoded}"


def _get_profile_image(user_id: str) -> Optional[str]:
    if not user_id:
        return None
    candidate = IMAGES_DIR / f"{user_id}.jpg"
    return _image_as_data_uri(candidate)


def show_profile_card(user: dict) -> None:
    """Display the profile card with avatar and key details."""

    user_id = user.get("user_id", "")
    image_data_uri = _get_profile_image(user_id)

    tag_html = _render_tags(_safe_split(user.get("skill_name", [])))

    st.markdown(
        f"""
        <div class="card profile-card">
            <div>
                {'<img src="' + image_data_uri + '" alt="Profile photo">' if image_data_uri else '<div class="pill">No photo</div>'}
            </div>
            <div>
                <h4>{user.get('first_name', '')} {user.get('last_name', '')}</h4>
                <p><strong>🎓 Major:</strong> {user.get('major', '-')}</p>
                <p><strong>📍 Location:</strong> {user.get('city', '-')}</p>
                <p><strong>🎯 Degree:</strong> {user.get('degree_type', '-')} &nbsp;|&nbsp; <strong>GPA:</strong> {user.get('gpa', '-')}</p>
                <div class="tag-list">{tag_html or '<span class="pill">Skills updating...</span>'}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_job_cards(jobs_df: pd.DataFrame) -> None:
    """Render job recommendations as friendly cards."""

    for _, row in jobs_df.iterrows():
        skills = _render_tags(_safe_split(row.get("proj_quals", "")))
        st.markdown(
            f"""
            <div class="card">
                <h4>✨ Job match: {row.get('jid', 'Unknown')}</h4>
                <p>These are the core skills that align with you:</p>
                <div class="tag-list">{skills or '<span class="pill">Skills unavailable</span>'}</div>
                <div class="card-footer">
                    <span>Recommended based on your profile</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_course_cards(recs_df: pd.DataFrame) -> None:
    """Render learning recommendations as friendly cards."""

    for _, course in recs_df.iterrows():
        taught = _render_tags(_safe_split(course.get("skills_taught", "")))
        st.markdown(
            f"""
            <div class="card">
                <h4>{course.get('course_name', 'Untitled course')}</h4>
                <p><strong>Provider:</strong> {course.get('provider', 'N/A')}</p>
                <p><strong>Duration:</strong> {course.get('duration_hours', 'N/A')} hours</p>
                <p><strong>Rating:</strong> {course.get('rating', 'N/A')} ⭐</p>
                <p>You'll sharpen these skills:</p>
                <div class="tag-list">{taught or '<span class="pill">Skills unavailable</span>'}</div>
                <div class="card-footer">
                    <span>Match score</span>
                    <span>{float(course.get('score', 0.0)) * 100:.0f}% fit</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
