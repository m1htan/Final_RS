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
    subset = merged[merged["user_id"] == user_id]
    return subset[["jid", "proj_quals"]].head(n)

def recommend_for_user(data, user_id):
    recs = data.get("recommendations", {})
    if user_id not in recs:
        return pd.DataFrame()
    df = pd.DataFrame(recs[user_id])
    df["score"] = df["score"].astype(float)
    return df.sort_values(by="score", ascending=False)
