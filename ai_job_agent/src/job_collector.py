import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = PROJECT_ROOT / "config" / "user_profile.json"
RAW_JOBS_PATH = PROJECT_ROOT / "data" / "raw_jobs.csv"


NON_TARGET_KEYWORDS = [
    "recruiter",
    "recruitment",
    "talent acquisition",
    "sales",
    "account executive",
    "customer support",
    "marketing manager",
]


def load_user_profile():
    """Load the job-search preferences used by the pipeline."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(f"Profile file not found at: {PROFILE_PATH}")

    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_html(text):
    """Remove basic HTML tags and normalize whitespace."""
    if not text:
        return ""

    clean_text = re.sub(r"<.*?>", " ", str(text))
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text.strip()


def normalize_text(*parts):
    return " ".join(str(part or "") for part in parts).lower()


def contains_keyword(text, keywords):
    return any(str(keyword).lower() in text for keyword in keywords)


def is_relevant_job(job, profile):
    """Apply strict first-pass filtering before ranking."""
    title = str(job.get("job_title", "")).lower()
    location = str(job.get("location", "")).lower()
    description = str(job.get("description", "")).lower()
    tags = str(job.get("tags", "")).lower()
    full_text = normalize_text(title, location, description, tags)

    target_roles = [role.lower() for role in profile.get("target_roles", [])]
    skills = [skill.lower() for skill in profile.get("skills", [])]
    target_locations = [loc.lower() for loc in profile.get("target_locations", [])]
    avoid_keywords = [word.lower() for word in profile.get("avoid_keywords", [])]
    experience_levels = [level.lower() for level in profile.get("experience_level", [])]

    if contains_keyword(title, avoid_keywords):
        return False

    if contains_keyword(full_text, NON_TARGET_KEYWORDS):
        return False

    role_match = contains_keyword(title, target_roles) or contains_keyword(full_text, target_roles)
    skill_match = contains_keyword(full_text, skills)
    location_match = contains_keyword(location, target_locations) or contains_keyword(full_text, target_locations)
    remote_match = job.get("remote", False) is True or "remote" in full_text or "hybrid" in full_text
    entry_level_match = contains_keyword(full_text, experience_levels)

    has_job_family = any(word in full_text for word in [
        "data", "analyst", "analytics", "bi", "machine learning", "ai", "research", "sql", "reporting"
    ])

    return has_job_family and (role_match or skill_match) and (location_match or remote_match or entry_level_match)


def fetch_jobs_from_arbeitnow():
    """Fetch jobs from the Arbeitnow free job API."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    jobs = response.json().get("data", [])
    cleaned_jobs = []

    for job in jobs:
        cleaned_jobs.append({
            "job_title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("location", ""),
            "remote": job.get("remote", False),
            "job_url": job.get("url", ""),
            "tags": ", ".join(job.get("tags", [])) if job.get("tags") else "",
            "job_types": ", ".join(job.get("job_types", [])) if job.get("job_types") else "",
            "description": clean_html(job.get("description", "")),
            "source": "Arbeitnow",
            "found_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return cleaned_jobs


def remove_duplicates(jobs):
    df = pd.DataFrame(jobs)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["job_url"], keep="first")


def merge_with_existing_jobs(new_df, output_path=RAW_JOBS_PATH):
    """Keep existing jobs and append only jobs with new URLs."""
    if new_df.empty:
        return new_df, 0

    if not output_path.exists():
        return new_df.drop_duplicates(subset=["job_url"], keep="first"), len(new_df)

    existing_df = pd.read_csv(output_path)
    existing_urls = set(existing_df.get("job_url", pd.Series(dtype=str)).fillna("").astype(str))
    new_only_df = new_df[~new_df["job_url"].fillna("").astype(str).isin(existing_urls)]
    combined_df = pd.concat([existing_df, new_only_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["job_url"], keep="first")
    return combined_df, len(new_only_df)


def save_jobs_to_csv(df, output_path=RAW_JOBS_PATH):
    output_path.parent.mkdir(exist_ok=True)
    combined_df, new_count = merge_with_existing_jobs(df, output_path)
    combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved raw jobs to {output_path}")
    print(f"New jobs added: {new_count}")
    print(f"Total unique raw jobs: {len(combined_df)}")
    return combined_df


def collect_jobs():
    print("Loading user profile...")
    profile = load_user_profile()

    print("Fetching jobs from Arbeitnow...")
    jobs = fetch_jobs_from_arbeitnow()
    print(f"Total jobs fetched: {len(jobs)}")

    relevant_jobs = [job for job in jobs if is_relevant_job(job, profile)]
    print(f"Relevant jobs after filtering: {len(relevant_jobs)}")

    df = remove_duplicates(relevant_jobs)
    if df.empty:
        print("No relevant jobs found after filtering.")
        return pd.read_csv(RAW_JOBS_PATH) if RAW_JOBS_PATH.exists() else df

    combined_df = save_jobs_to_csv(df)
    print("Job collection completed successfully.")
    return combined_df


def main():
    collect_jobs()


if __name__ == "__main__":
    main()
