import base64
import json
import re
from html import escape
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
from textwrap import dedent

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = REPO_ROOT / "images"


def _render_tags(items: Iterable[str]) -> str:
    tags = [f"<span class='pill'>{escape(item.strip())}</span>" for item in items if item and item.strip()]
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
    """Render each skill row as single-line HTML (no newline, no indent)."""
    rows = []
    for name, raw_level in _pair_skills(user):
        details = _LEVEL_DETAILS.get(raw_level.strip().upper(), {"label": "Unknown", "score": 10})
        row = (
            "<div class='skill-row'>"
            "<div class='skill-info'>"
            f"<span class='skill-name'>{name}</span>"
            f"<span class='skill-level'>{details['label']}</span>"
            "</div>"
            "<div class='progress-track'>"
            f"<div class='progress-bar' style='width:{details['score']}%'></div>"
            "</div>"
            "</div>"
        )
        rows.append(row)
    return "".join(rows)


def show_profile_card(user: dict) -> None:
    """Display the profile view in Streamlit with real HTML rendering."""
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

    # Render skill section
    skills_markup = _render_skill_rows(user)
    if not skills_markup:
        skills_markup = "<div class='empty-copy'>No skills registered yet.</div>"

    skill_pairs = _pair_skills(user)
    total_skills = len(skill_pairs)
    tracked_levels = [
        _LEVEL_DETAILS.get(level.strip().upper(), {"score": 0})["score"]
        for _, level in skill_pairs
    ]
    avg_level = int(round(sum(tracked_levels) / total_skills)) if total_skills else 0

    # HTML content (no indent)
    html = f"""
<div class="profile-page">

<section class="card profile-header">
    <div class="profile-avatar">
        {f'<img src="{image_data_uri}" alt="Profile photo" />' if image_data_uri else f"<div class='avatar-fallback'>{initials}</div>"}
    </div>
    <div class="profile-summary">
        <h2>{full_name}</h2>
        <p class="profile-role">{major or 'Specialisation unavailable'}</p>
        <div class="profile-meta">
            <div class="meta-item"><span class="meta-label">Employee ID</span><span class="meta-value">{user_id or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">Degree</span><span class="meta-value">{degree or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">GPA</span><span class="meta-value">{gpa or '—'}</span></div>
            <div class="meta-item"><span class="meta-label">Location</span><span class="meta-value">{city or '—'}</span></div>
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
        <div><span class="detail-label">First name</span><span class="detail-value">{first_name or '—'}</span></div>
        <div><span class="detail-label">Last name</span><span class="detail-value">{last_name or '—'}</span></div>
        <div><span class="detail-label">Specialisation</span><span class="detail-value">{major or '—'}</span></div>
        <div><span class="detail-label">Highest degree</span><span class="detail-value">{degree or '—'}</span></div>
        <div><span class="detail-label">Current city</span><span class="detail-value">{city or '—'}</span></div>
        <div><span class="detail-label">GPA</span><span class="detail-value">{gpa or '—'}</span></div>
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
            <h3>Development recommendations</h3>
            <p class="section-description">Explore tailored job matches and courses to continue professional growth.</p>
        </div>
    </div>
    <div class="detail-grid single-column">
        <div>
            <span class="detail-label">Job matches</span>
            <span class="detail-value">Review the <strong>Job Match</strong> tab for roles that align with this profile.</span>
        </div>
        <div>
            <span class="detail-label">Learning path</span>
            <span class="detail-value">Visit the <strong>Learning Path</strong> tab to identify courses that close remaining skill gaps.</span>
        </div>
    </div>
</section>

</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def show_job_cards(jobs_df: pd.DataFrame) -> Optional[str]:
    """Render job recommendations as modern cards with linked titles."""

    def _job_identifier(row: pd.Series, fallback: int) -> str:
        for key in ("jid", "job_id", "id"):
            if key in row and pd.notna(row[key]):
                value = str(row[key]).strip()
                if value:
                    return value
        return str(fallback)

    selected_job_id = st.session_state.get("selected_job_id")
    selected_job_id = str(selected_job_id) if selected_job_id is not None else None

    for index, row in jobs_df.iterrows():
        job_id = _job_identifier(row, index)
        is_active = selected_job_id == job_id

        raw_job_title = (
            row.get("job_title")
            or row.get("title")
            or row.get("jid")
            or "Untitled role"
        )
        job_title = escape(str(raw_job_title))
        company = escape(str(row.get("company") or "Unknown company"))
        location = escape(str(row.get("location") or "Location not specified"))
        employment_type = escape(
            str(row.get("employment_type") or row.get("job_type") or "Full-time")
        )
        salary = escape(
            str(row.get("salary_range") or row.get("salary") or "Salary not disclosed")
        )
        experience = escape(
            str(row.get("experience_level") or row.get("level") or "All levels")
        )
        posted = escape(str(row.get("posted") or row.get("timeline") or "Just posted"))

        score = row.get("score")
        score_value = None
        if pd.notna(score):
            try:
                numeric_score = float(score)
                score_value = numeric_score * 100 if numeric_score <= 1 else numeric_score
            except (TypeError, ValueError):
                score_value = None

        match_label = f"Match {score_value:.0f}%" if score_value is not None else "Match —"

        skills = _render_tags(_safe_split(row.get("proj_quals", "")))
        if not skills:
            skills = "<span class='pill muted'>Skills unavailable</span>"

        initials_source = row.get("company") or raw_job_title
        initials = (
            str(initials_source)[:1].upper()
            if initials_source and str(initials_source).strip()
            else "J"
        )

        card_classes = "job-card"
        if is_active:
            card_classes += " is-active"

        highlights = dedent(
            f"""
            <div class='job-card-highlights'>
                <span class='pill soft'>{employment_type}</span>
                <span class='pill soft'>{experience}</span>
                <span class='pill muted'>{salary}</span>
                <span class='pill muted'>{posted}</span>
            </div>
            """
        ).strip()

        card_html = dedent(
            f"""
            <article class="{card_classes}">
                <div class="job-card-leading">
                    <div class="job-card-badge" aria-hidden="true">{escape(initials)}</div>
                </div>
                <div class="job-card-content">
                    <div class="job-card-header">
                        <div class="job-card-title">
                            <a class="job-card-link" href="#" data-job-id="{escape(job_id)}" role="link">{job_title}</a>
                        </div>
                        <span class="match-chip">{match_label}</span>
                    </div>
                    <div class="job-card-meta">
                        <span>{company}</span>
                        <span class="dot"></span>
                        <span>{location}</span>
                    </div>
                    {highlights}
                    <div class="job-card-skills" aria-label="Key skills">{skills}</div>
                </div>
            </article>
            """
        ).strip()

        st.markdown(card_html, unsafe_allow_html=True)

    selection = components.html(
        """
        <script>
        const Streamlit = window.parent.Streamlit || window.Streamlit;
        const doc = window.parent.document;

        function wireJobLinks() {
            const links = doc.querySelectorAll('a.job-card-link[data-job-id]');
            links.forEach((link) => {
                if (link.dataset.listenerAttached === 'true') {
                    return;
                }
                link.dataset.listenerAttached = 'true';
                link.addEventListener('click', (event) => {
                    event.preventDefault();
                    const jobId = link.getAttribute('data-job-id');
                    if (Streamlit && jobId) {
                        const payload = {
                            jobId: jobId,
                            nonce: `${Date.now()}_${Math.random().toString(16).slice(2)}`
                        };
                        Streamlit.setComponentValue(JSON.stringify(payload));
                    }
                });
            });
        }

        wireJobLinks();

        const observer = new MutationObserver(() => {
            wireJobLinks();
        });
        observer.observe(doc.body, { childList: true, subtree: true });

        if (Streamlit && Streamlit.setComponentReady) {
            Streamlit.setComponentReady();
        }
        if (Streamlit && Streamlit.setFrameHeight) {
            Streamlit.setFrameHeight(0);
        }
        </script>
        """,
        height=0,
        scrolling=False,
    )

    if selection:
        job_id = None
        nonce = None
        if isinstance(selection, str):
            try:
                payload = json.loads(selection)
            except (json.JSONDecodeError, TypeError):
                payload = None

            if isinstance(payload, dict):
                job_id = payload.get("jobId") or payload.get("job_id") or payload.get("id")
                nonce = payload.get("nonce")
            else:
                job_id = selection
        else:
            job_id = str(selection)

        if job_id:
            job_id = str(job_id)
            last_nonce = st.session_state.get("job_click_nonce")
            if nonce and nonce != last_nonce:
                st.session_state["job_click_nonce"] = nonce
                st.session_state["selected_job_id"] = job_id
                st.session_state["job_detail_mode"] = True
                st.session_state["job_match_view"] = "detail"
            elif not nonce and job_id != st.session_state.get("selected_job_id"):
                st.session_state["selected_job_id"] = job_id
                st.session_state["job_detail_mode"] = True
                st.session_state["job_match_view"] = "detail"

    return st.session_state.get("selected_job_id")


def _derive_job_highlights(description: Optional[str]) -> Tuple[str, List[str]]:
    if not description or (isinstance(description, float) and pd.isna(description)):
        return "Job overview is not available for this role yet.", []

    text = str(description)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    segments = [segment.strip("•- \u2022") for segment in text.split("\n") if segment.strip()]

    if not segments:
        cleaned = re.split(r"(?<=[.!?])\s+", text)
        segments = [segment.strip("•- ") for segment in cleaned if segment.strip()]

    if not segments:
        return "Job overview is not available for this role yet.", []

    overview = segments[0]
    responsibilities = segments[1:] or []
    return overview, responsibilities


def show_job_detail(job: Optional[pd.Series]) -> None:
    """Render a detailed job preview panel."""

    if job is None:
        st.markdown(
            "<div class='job-detail-empty card'>Select a job from the list to view its full description.</div>",
            unsafe_allow_html=True,
        )
        return

    if isinstance(job, pd.Series):
        job_data = job.to_dict()
    else:
        job_data = job or {}

    def _clean(value: Optional[str], fallback: str = "—") -> str:
        if value is None:
            return fallback
        if isinstance(value, float) and pd.isna(value):
            return fallback
        text = str(value).strip()
        return text or fallback

    raw_job_title = _clean(job_data.get("job_title") or job_data.get("title"), "Untitled role")
    raw_company = _clean(job_data.get("company"), "Unknown company")
    job_title = escape(raw_job_title)
    company = escape(raw_company)
    location = escape(_clean(job_data.get("location"), "Location not specified"))
    employment_type = escape(_clean(job_data.get("employment_type") or job_data.get("job_type"), "Full-time"))
    salary = escape(_clean(job_data.get("salary_range") or job_data.get("salary"), "Not disclosed"))
    experience = escape(_clean(job_data.get("experience_level") or job_data.get("level"), "All levels"))
    start_date = escape(_clean(job_data.get("start_date"), "Immediate"))
    end_date = escape(_clean(job_data.get("end_date"), "Open until filled"))

    overview, bullets = _derive_job_highlights(job_data.get("job_desc"))
    overview_html = f"<p>{escape(overview)}</p>" if overview else ""

    responsibilities = [escape(item) for item in bullets[:4]]
    preferred = [escape(item) for item in bullets[4:8]]

    responsibilities_html = (
        "<ul class='detail-list'>" + "".join(f"<li>{item}</li>" for item in responsibilities) + "</ul>"
        if responsibilities
        else "<div class='empty-copy'>Responsibilities will be shared soon.</div>"
    )

    preferred_html = (
        "<ul class='detail-list'>" + "".join(f"<li>{item}</li>" for item in preferred) + "</ul>"
        if preferred
        else "<div class='empty-copy'>Preferred qualifications will be updated shortly.</div>"
    )

    qualification_tags = _render_tags(_safe_split(job_data.get("proj_quals", "")))
    if not qualification_tags:
        qualification_tags = "<div class='empty-copy'>This role has no specific skills listed yet.</div>"

    match_score = job_data.get("score")
    if pd.notna(match_score):
        try:
            match_value = float(match_score) * 100 if float(match_score) <= 1 else float(match_score)
            match_display = f"{match_value:.0f}%"
        except (TypeError, ValueError):
            match_display = "—"
    else:
        match_display = "—"

    benefits = [
        "Competitive compensation package",
        "Flexible work arrangements and remote-friendly culture",
        "Comprehensive health and wellness benefits",
    ]
    benefits_html = "<ul class='detail-list'>" + "".join(f"<li>{escape(item)}</li>" for item in benefits) + "</ul>"

    about_team = f"Join {company} to collaborate with a cross-functional team focused on delivering impactful digital experiences."
    contact_domain = re.sub(r"[^a-z0-9]", "", raw_company.lower()) or "company"

    detail_html = f"""
    <div class="job-detail-wrapper">
        <div class="job-detail-main">
            <article class="detail-card">
                <header class="detail-header">
                    <h2>{job_title}</h2>
                    <p>{company} • {location} • {employment_type}</p>
                </header>
                <section class="detail-section">
                    <h3>Job Overview</h3>
                    {overview_html}
                </section>
                <section class="detail-section">
                    <h3>Job Responsibilities</h3>
                    {responsibilities_html}
                </section>
                <section class="detail-section">
                    <h3>Required Skills &amp; Qualifications</h3>
                    <div class="tag-list">{qualification_tags}</div>
                </section>
                <section class="detail-section">
                    <h3>Preferred Qualifications</h3>
                    {preferred_html}
                </section>
                <section class="detail-section">
                    <h3>What We Offer</h3>
                    {benefits_html}
                </section>
                <section class="detail-section">
                    <h3>About the Team</h3>
                    <p>{about_team}</p>
                </section>
            </article>
        </div>
        <aside class="job-detail-sidebar">
            <div class="job-summary-card">
                <div class="summary-group">
                    <span class="summary-label">Location</span>
                    <span class="summary-value">{location}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Employment type</span>
                    <span class="summary-value">{employment_type}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Experience level</span>
                    <span class="summary-value">{experience}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Salary range</span>
                    <span class="summary-value">{salary}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Start date</span>
                    <span class="summary-value">{start_date}</span>
                </div>
                <div class="summary-group">
                    <span class="summary-label">Closing date</span>
                    <span class="summary-value">{end_date}</span>
                </div>
                <div class="summary-group highlight">
                    <span class="summary-label">Your match score</span>
                    <span class="summary-value score">{match_display}</span>
                </div>
                <button class="apply-button" type="button">Apply now</button>
            </div>
            <div class="sidebar-card">
                <h4>Recruiter information</h4>
                <p class="sidebar-text">Have questions? Reach out to the talent team for more details about the role and interview process.</p>
                <div class="contact-chip">talent@{contact_domain}.com</div>
            </div>
        </aside>
    </div>
    """

    st.markdown(detail_html, unsafe_allow_html=True)


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
