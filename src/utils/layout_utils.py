import base64
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

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


def _initials(user: dict) -> str:
    first = str(user.get("first_name", "")).strip()[:1]
    last = str(user.get("last_name", "")).strip()[:1]
    initials = (first + last).upper()
    return initials or "SG"


def _pair_skills(user: dict) -> List[Tuple[str, str]]:
    names = _safe_split(user.get("skill_name", []))
    levels = _safe_split(user.get("skill_level", []))
    if len(levels) < len(names):
        levels.extend([""] * (len(names) - len(levels)))
    elif len(levels) > len(names):
        names.extend(["Skill"] * (len(levels) - len(names)))
    return list(zip(names, levels))


_LEVEL_DETAILS = {
    "L1": {"label": "Beginner", "score": 25},
    "L2": {"label": "Intermediate", "score": 50},
    "L3": {"label": "Advanced", "score": 75},
    "L4": {"label": "Expert", "score": 100},
}


def _render_skill_rows(user: dict) -> str:
    rows = []
    for name, raw_level in _pair_skills(user):
        details = _LEVEL_DETAILS.get(raw_level.strip().upper(), {"label": "Unknown", "score": 10})
        rows.append(
            f"""
            <div class='skill-row'>
                <div class='skill-info'>
                    <span class='skill-name'>{name}</span>
                    <span class='skill-level'>{details['label']}</span>
                </div>
                <div class='progress-track'>
                    <div class='progress-bar' style='width:{details['score']}%'></div>
                </div>
            </div>
            """
        )
    return "".join(rows)


def show_profile_card(user: dict) -> None:
    """Display the profile view, inspired by the design reference."""

    user_id = user.get("user_id", "")
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip() or "Unnamed employee"
    image_data_uri = _get_profile_image(user_id)
    initials = _initials(user)
    gpa = user.get("gpa", "-")
    degree = user.get("degree_type", "-")
    major = user.get("major", "-")
    city = user.get("city", "-")

    skills_markup = _render_skill_rows(user)
    if not skills_markup:
        skills_markup = "<div class='empty-copy'>No skills registered yet.</div>"

    skill_pairs = _pair_skills(user)
    total_skills = len(skill_pairs)
    tracked_levels = [
        _LEVEL_DETAILS.get(level.strip().upper(), {"score": 0}).get("score", 0)
        for _, level in skill_pairs
    ]
    avg_level = int(round(sum(tracked_levels) / total_skills)) if total_skills else 0

    st.markdown(
        f"""
        <div class="profile-page">
            <section class="card profile-header">
                <div class="profile-avatar">
                    {'<img src="' + image_data_uri + '" alt="Profile photo" />' if image_data_uri else f"<div class='avatar-fallback'>{initials}</div>"}
                </div>
                <div class="profile-summary">
                    <h2>{full_name}</h2>
                    <p class="profile-role">{major or 'Specialisation unavailable'}</p>
                    <div class="profile-meta">
                        <div class="meta-item">
                            <span class="meta-label">Employee ID</span>
                            <span class="meta-value">{user_id or '—'}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Degree</span>
                            <span class="meta-value">{degree or '—'}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">GPA</span>
                            <span class="meta-value">{gpa or '—'}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Location</span>
                            <span class="meta-value">{city or '—'}</span>
                        </div>
                    </div>
                </div>
                <div class="profile-actions">
                    <button class="button ghost">View performance</button>
                </div>
            </section>

            <section class="profile-highlights">
                <div class="mini-card">
                    <span class="mini-label">Skills tracked</span>
                    <span class="mini-value">{total_skills}</span>
                    <span class="mini-caption">Declared competencies</span>
                </div>
                <div class="mini-card">
                    <span class="mini-label">Average proficiency</span>
                    <span class="mini-value">{avg_level}%</span>
                    <span class="mini-caption">Across registered skills</span>
                </div>
                <div class="mini-card">
                    <span class="mini-label">Academic score</span>
                    <span class="mini-value">{gpa or '—'}</span>
                    <span class="mini-caption">Latest reported GPA</span>
                </div>
            </section>

            <section class="card section-card">
                <div class="section-header">
                    <div>
                        <h3>Employee overview</h3>
                        <p class="section-description">Key background information pulled from the employee registry.</p>
                    </div>
                </div>
                <div class="detail-grid">
                    <div>
                        <span class="detail-label">First name</span>
                        <span class="detail-value">{first_name or '—'}</span>
                    </div>
                    <div>
                        <span class="detail-label">Last name</span>
                        <span class="detail-value">{last_name or '—'}</span>
                    </div>
                    <div>
                        <span class="detail-label">Specialisation</span>
                        <span class="detail-value">{major or '—'}</span>
                    </div>
                    <div>
                        <span class="detail-label">Highest degree</span>
                        <span class="detail-value">{degree or '—'}</span>
                    </div>
                    <div>
                        <span class="detail-label">Current city</span>
                        <span class="detail-value">{city or '—'}</span>
                    </div>
                    <div>
                        <span class="detail-label">GPA</span>
                        <span class="detail-value">{gpa or '—'}</span>
                    </div>
                </div>
            </section>

            <section class="card section-card">
                <div class="section-header">
                    <div>
                        <h3>Skill proficiency</h3>
                        <p class="section-description">Latest proficiency ratings for each declared skill.</p>
                    </div>
                </div>
                <div class="skill-matrix">{skills_markup}</div>
            </section>

            <section class="card section-card">
                <div class="section-header">
                    <div>
                        <h3>Next best actions</h3>
                        <p class="section-description">Bridge the gap between current skills and future opportunities with these personalised steps.</p>
                    </div>
                </div>
                <div class="action-grid">
                    <div class="action-card job-action">
                        <div class="action-icon">💼</div>
                        <div class="action-content">
                            <h4>Review job matches</h4>
                            <p>Head to the <strong>Job Match</strong> tab to explore tailored roles, compare fit scores, and shortlist your next move.</p>
                        </div>
                        <a class="action-link" href="#job-match">Open tab</a>
                    </div>
                    <div class="action-card learning-action">
                        <div class="action-icon">🎓</div>
                        <div class="action-content">
                            <h4>Strengthen your skills</h4>
                            <p>Browse the <strong>Learning Path</strong> tab to find curated courses that close remaining gaps and boost your readiness.</p>
                        </div>
                        <a class="action-link" href="#learning-path">Open tab</a>
                    </div>
                </div>
            </section>
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
