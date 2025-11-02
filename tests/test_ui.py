import streamlit as st
import pandas as pd
from html import escape
from textwrap import dedent


# ======== HÀM PHỤ ========
def _render_tags(items):
    """Render danh sách kỹ năng thành các thẻ nhỏ"""
    tags = [f"<span class='pill'>{escape(item.strip())}</span>" for item in items if item and item.strip()]
    return "".join(tags)


def _safe_split(value):
    """Tách chuỗi kỹ năng cách nhau bằng dấu phẩy"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [piece.strip() for piece in str(value).split(",") if piece.strip()]


# ======== HÀM CHÍNH ========
def show_job_cards(jobs_df: pd.DataFrame):
    def _job_identifier(row, fallback):
        for key in ("jid", "job_id", "id"):
            if key in row and pd.notna(row[key]):
                return str(row[key]).strip()
        return str(fallback)

    active_job_id = st.session_state.get("selected_job_id")
    active_job_id = str(active_job_id) if active_job_id is not None else None

    for index, row in jobs_df.iterrows():
        job_id = _job_identifier(row, index)
        is_active = active_job_id == job_id

        job_title = escape(str(row.get("job_title", "Untitled role")))
        company = escape(str(row.get("company", "Unknown company")))
        location = escape(str(row.get("location", "Location not specified")))
        employment_type = escape(str(row.get("employment_type", "Full-time")))
        salary = escape(str(row.get("salary", "Salary not disclosed")))
        experience = escape(str(row.get("experience_level", "All levels")))
        posted = escape(str(row.get("posted", "Just posted")))

        score = row.get("score", None)
        if pd.notna(score):
            try:
                score_value = float(score)
                score_value = score_value * 100 if score_value <= 1 else score_value
                match_label = f"Match {score_value:.0f}%"
            except Exception:
                match_label = "Match —"
        else:
            match_label = "Match —"

        skills = _render_tags(_safe_split(row.get("skills", ""))) or "<span class='pill muted'>No skills listed</span>"

        card_classes = "job-card"
        if is_active:
            card_classes += " is-active"

        highlights = dedent(f"""
            <div class='job-card-highlights'>
                <span class='pill soft'>{employment_type}</span>
                <span class='pill soft'>{experience}</span>
                <span class='pill muted'>{salary}</span>
                <span class='pill muted'>{posted}</span>
            </div>
        """).strip()

        card_html = dedent(f"""
            <article class="{card_classes}">
                <div class="job-card-content">
                    <div class="job-card-header">
                        <div class="job-card-title">
                            <span style="font-weight:600; color:#0073e6;">{job_title}</span>
                        </div>
                        <span class="match-chip">{match_label}</span>
                    </div>
                    <div class="job-card-meta">
                        <span>{company}</span> • <span>{location}</span>
                    </div>
                    {highlights}
                    <div class="job-card-skills">{skills}</div>
                </div>
            </article>
        """).strip()

        st.markdown(card_html, unsafe_allow_html=True)

        # Nút vô hình để click
        if st.button(f"🔍 Xem chi tiết: {job_title}", key=f"btn_{job_id}"):
            st.session_state.selected_job_id = job_id
            st.rerun()

        if is_active:
            st.info(f"📄 Chi tiết công việc: **{job_title}** tại {company}\n\nYêu cầu: {row.get('skills')}")
            if st.button("❌ Ẩn chi tiết", key=f"hide_{job_id}"):
                st.session_state.selected_job_id = None
                st.rerun()
            st.markdown("---")


# ======== CHẠY DEMO ========
st.set_page_config(page_title="Job Card Demo", layout="wide")

st.title("💼 Mô phỏng giao diện show_job_cards()")

# Data giả lập
jobs = pd.DataFrame([
    {
        "job_id": "J001",
        "job_title": "Data Analyst",
        "company": "Motives Tech",
        "location": "Ho Chi Minh City",
        "employment_type": "Full-time",
        "salary": "25–35M VND",
        "experience_level": "Mid-level",
        "posted": "3 days ago",
        "skills": "Python, SQL, Power BI, Excel",
        "score": 0.87,
    },
    {
        "job_id": "J002",
        "job_title": "AI Research Intern",
        "company": "LawInTech",
        "location": "Hanoi",
        "employment_type": "Internship",
        "salary": "Negotiable",
        "experience_level": "Entry",
        "posted": "Just posted",
        "skills": "LangChain, Python, Transformers",
        "score": 0.95,
    },
    {
        "job_id": "J003",
        "job_title": "ERP Consultant",
        "company": "Guangwei Vietnam",
        "location": "Binh Duong",
        "employment_type": "Full-time",
        "salary": "30–40M VND",
        "experience_level": "Senior",
        "posted": "1 week ago",
        "skills": "U9 Cloud, SQL, Manufacturing, Costing",
        "score": 0.82,
    },
])

# Gọi hàm
show_job_cards(jobs)


# ======== CSS ========
st.markdown("""
<style>
.job-card {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    transition: box-shadow 0.3s;
    background: #fff;
}
.job-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.job-card.is-active {
    border-color: #0073e6;
    box-shadow: 0 0 10px rgba(0,115,230,0.3);
}
.pill {
    display: inline-block;
    padding: 2px 8px;
    margin-right: 4px;
    border-radius: 10px;
    font-size: 12px;
}
.soft { background: #f0f7ff; color: #0073e6; }
.muted { background: #f6f6f6; color: #888; }
.job-card-meta { color: #666; font-size: 14px; margin-top: 4px; }
.match-chip { font-weight: 600; color: #0073e6; }
.job-card-skills { margin-top: 8px; }
</style>
""", unsafe_allow_html=True)
