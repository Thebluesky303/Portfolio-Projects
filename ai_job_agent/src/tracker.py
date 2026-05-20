from pathlib import Path
from datetime import datetime

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RANKED_JOBS_PATH = PROJECT_ROOT / "data" / "ranked_jobs.csv"
TRACKER_PATH = PROJECT_ROOT / "data" / "application_tracker.csv"


MANUAL_COLUMNS = ["status", "approval_status", "applied_date", "last_updated", "notes"]


def load_ranked_jobs(path=RANKED_JOBS_PATH):
    if not path.exists():
        raise FileNotFoundError("ranked_jobs.csv not found. Run job_ranker.py first.")
    return pd.read_csv(path)


def status_from_recommendation(recommendation):
    if recommendation in ["Apply First", "Strong Review"]:
        return "Shortlisted"
    if recommendation in ["Review Later", "Low Priority"]:
        return "Saved for Later"
    return "Ignored"


def create_application_tracker(ranked_jobs=None):
    ranked_jobs = ranked_jobs if ranked_jobs is not None else load_ranked_jobs()
    tracker_rows = []

    for _, job in ranked_jobs.iterrows():
        recommendation = job.get("recommendation", "Skip")
        tracker_rows.append({
            "job_title": job.get("job_title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_url": job.get("job_url", ""),
            "source": job.get("source", ""),
            "match_score": job.get("match_score", 0),
            "match_level": job.get("match_level", ""),
            "ranking_score": job.get("ranking_score", 0),
            "recommendation": recommendation,
            "ranking_reason": job.get("ranking_reason", ""),
            "matched_skills": job.get("matched_skills", ""),
            "missing_skills": job.get("missing_skills", ""),
            "status": status_from_recommendation(recommendation),
            "approval_status": "Not Reviewed",
            "applied_date": "",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": "",
        })

    tracker_df = pd.DataFrame(tracker_rows)
    if not tracker_df.empty:
        tracker_df = tracker_df.drop_duplicates(subset=["job_url"], keep="first")
    return tracker_df


def merge_with_existing_tracker(new_df, output_path=TRACKER_PATH):
    """Append new jobs while keeping existing manual review fields unchanged."""
    if new_df.empty:
        return new_df, 0

    if not output_path.exists():
        return new_df.drop_duplicates(subset=["job_url"], keep="first"), len(new_df)

    existing_df = pd.read_csv(output_path)
    existing_urls = set(existing_df.get("job_url", pd.Series(dtype=str)).fillna("").astype(str))
    new_only_df = new_df[~new_df["job_url"].fillna("").astype(str).isin(existing_urls)].copy()

    for column in existing_df.columns:
        if column not in new_only_df.columns:
            new_only_df.loc[:, column] = ""

    combined_df = pd.concat([existing_df, new_only_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["job_url"], keep="first")

    if "ranking_score" in combined_df.columns:
        combined_df = combined_df.sort_values(by="ranking_score", ascending=False)

    return combined_df, len(new_only_df)


def save_tracker(tracker_df, output_path=TRACKER_PATH):
    output_path.parent.mkdir(exist_ok=True)
    combined_df, new_count = merge_with_existing_tracker(tracker_df, output_path)
    combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Application tracker saved to: {output_path}")
    print(f"New tracker jobs added: {new_count}")
    print(f"Total unique tracked jobs: {len(combined_df)}")
    return combined_df


def main():
    print("Creating application tracker...")
    tracker_df = create_application_tracker()

    if tracker_df.empty:
        print("No jobs available for tracker.")
        return

    combined_df = save_tracker(tracker_df)
    print("\nTracker summary:")
    print(combined_df["status"].value_counts())
    print("\nApplication tracker created successfully.")


if __name__ == "__main__":
    main()

