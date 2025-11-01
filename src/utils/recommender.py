import joblib
import pandas as pd

def load_model():
    """
    Load serialized model data (MiniLM recommender .pkl)
    Expected keys:
        - employee_df
        - job_df
        - course_df
        - merged
        - recommendations
    """
    data = joblib.load("/Users/minhtan/Documents/GitHub/RecommendationSystem/final/models/minilm_recommender_light.pkl")
    return data

def get_user_info(data, user_id):
    emp_df = data.get("employee_df", pd.DataFrame())
    info = emp_df[emp_df["user_id"] == user_id]
    return info.to_dict(orient="records")[0] if not info.empty else None

def top_jobs_for_user(data, user_id, n=5):
    merged = data.get("merged", pd.DataFrame())
    if merged.empty:
        return pd.DataFrame()

    subset = merged[merged["user_id"] == user_id].copy()

    job_df = data.get("job_df", pd.DataFrame())
    if not job_df.empty and "jid" in job_df.columns:
        # keep only relevant job columns to avoid duplicating heavy text fields
        optional_columns = [
            "job_title",
            "title",
            "location",
            "company",
            "employment_type",
            "job_type",
            "salary_range",
            "salary",
            "experience_level",
            "level",
            "job_desc",
            "start_date",
            "end_date",
        ]
        job_columns = ["jid"] + [col for col in optional_columns if col in job_df.columns]
        job_details = job_df[job_columns].drop_duplicates(subset=["jid"])
        subset = subset.merge(job_details, on="jid", how="left")

    if "job_title" not in subset.columns:
        if "title" in subset.columns:
            subset = subset.rename(columns={"title": "job_title"})
        else:
            if not job_df.empty and "jid" in job_df.columns:
                title_column = "job_title" if "job_title" in job_df.columns else None
                if not title_column and "title" in job_df.columns:
                    title_column = "title"
                if title_column:
                    title_map = job_df.set_index("jid")[title_column]
                    subset["job_title"] = subset["jid"].map(title_map)
        if "job_title" not in subset.columns:
            subset["job_title"] = subset["jid"]

    if "score" in subset.columns:
        subset = subset.sort_values(by="score", ascending=False, na_position="last")

    if "jid" in subset.columns:
        subset = subset.drop_duplicates(subset=["jid"], keep="first")

    desired_order = [
        "jid",
        "job_title",
        "proj_quals",
        "location",
        "company",
        "employment_type",
        "job_type",
        "salary_range",
        "salary",
        "experience_level",
        "level",
        "job_desc",
        "start_date",
        "end_date",
        "score",
    ]
    combined = subset.copy()

    if len(combined) < n and not job_df.empty:
        fallback_jobs = job_df.copy()

        if "job_title" not in fallback_jobs.columns and "title" in fallback_jobs.columns:
            fallback_jobs = fallback_jobs.rename(columns={"title": "job_title"})

        if "jid" in fallback_jobs.columns and "jid" in combined.columns:
            existing_ids = combined["jid"].astype(str).tolist()
            fallback_jobs = fallback_jobs[
                ~fallback_jobs["jid"].astype(str).isin(existing_ids)
            ]

        fallback_columns = [col for col in desired_order if col in fallback_jobs.columns]
        if fallback_columns:
            fallback_jobs = fallback_jobs[fallback_columns]
            fallback_jobs = fallback_jobs.head(max(n - len(combined), 0))

            if not fallback_jobs.empty:
                if "score" not in fallback_jobs.columns:
                    fallback_jobs["score"] = None

                combined = pd.concat([combined, fallback_jobs], ignore_index=True, sort=False)

    final_columns = [col for col in desired_order if col in combined.columns]
    if not final_columns:
        return pd.DataFrame()

    return combined[final_columns].head(n)

def recommend_for_user(data, user_id):
    recs = data.get("recommendations", {})
    if user_id not in recs:
        return pd.DataFrame()
    df = pd.DataFrame(recs[user_id])
    df["score"] = df["score"].astype(float)
    return df.sort_values(by="score", ascending=False)
