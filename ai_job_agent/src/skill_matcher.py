import json
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = PROJECT_ROOT / "config" / "user_profile.json"
RAW_JOBS_PATH = PROJECT_ROOT / "data" / "raw_jobs.csv"
MATCHED_JOBS_PATH = PROJECT_ROOT / "data" / "matched_jobs.csv"


ALIASES = {
    "Power BI": ["powerbi", "power bi"],
    "Scikit-learn": ["scikit learn", "sklearn", "scikit-learn"],
    "Data Visualisation": ["data visualisation", "data visualization", "visualisation", "visualization"],
    "GitHub": ["github", "git"],
    "Report Writing": ["report writing", "reporting", "reports"],
    "Machine Learning": ["machine learning", "ml"],
}


def load_user_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_jobs(path=RAW_JOBS_PATH):
    if not path.exists():
        raise FileNotFoundError("raw_jobs.csv not found. Run job_collector.py first.")
    return pd.read_csv(path)


def normalize_text(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def skill_terms(skill):
    return [skill.lower(), *ALIASES.get(skill, [])]


def find_matched_skills(job_text, user_skills):
    normalized = normalize_text(job_text)
    matched = []

    for skill in user_skills:
        if any(term in normalized for term in skill_terms(skill)):
            matched.append(skill)

    return matched


def calculate_match_score(matched_skills, total_skills):
    if total_skills == 0:
        return 0
    return round((len(matched_skills) / total_skills) * 100, 2)


def classify_match(score, thresholds=None):
    thresholds = thresholds or {"excellent": 85, "good": 70, "medium": 50}
    if score >= thresholds.get("excellent", 85):
        return "Excellent"
    if score >= thresholds.get("good", 70):
        return "Good"
    if score >= thresholds.get("medium", 50):
        return "Medium"
    return "Weak"


def build_job_text(job):
    return " ".join(str(job.get(column, "")) for column in [
        "job_title",
        "company",
        "location",
        "tags",
        "job_types",
        "description",
    ])


def match_jobs(jobs_df=None):
    profile = load_user_profile()
    jobs_df = jobs_df if jobs_df is not None else load_jobs()
    user_skills = profile.get("skills", [])
    thresholds = profile.get("match_thresholds", {})

    results = []
    for _, job in jobs_df.iterrows():
        job_text = build_job_text(job)
        matched_skills = find_matched_skills(job_text, user_skills)
        missing_skills = [skill for skill in user_skills if skill not in matched_skills]
        score = calculate_match_score(matched_skills, len(user_skills))

        row = job.to_dict()
        row.update({
            "match_score": score,
            "match_level": classify_match(score, thresholds),
            "matched_skills": ", ".join(matched_skills),
            "missing_skills": ", ".join(missing_skills),
            "status": "Found",
        })
        results.append(row)

    matched_df = pd.DataFrame(results)
    if not matched_df.empty:
        matched_df = matched_df.drop_duplicates(subset=["job_url"], keep="first")
        matched_df = matched_df.sort_values(by="match_score", ascending=False)
    return matched_df


def merge_with_existing_matches(new_df, output_path=MATCHED_JOBS_PATH):
    if new_df.empty:
        return new_df, 0

    if not output_path.exists():
        return new_df.drop_duplicates(subset=["job_url"], keep="first"), len(new_df)

    existing_df = pd.read_csv(output_path)
    existing_urls = set(existing_df.get("job_url", pd.Series(dtype=str)).fillna("").astype(str))
    new_only_df = new_df[~new_df["job_url"].fillna("").astype(str).isin(existing_urls)]
    combined_df = pd.concat([existing_df, new_only_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["job_url"], keep="first")
    combined_df = combined_df.sort_values(by="match_score", ascending=False)
    return combined_df, len(new_only_df)


def save_matched_jobs(df, output_path=MATCHED_JOBS_PATH):
    output_path.parent.mkdir(exist_ok=True)
    combined_df, new_count = merge_with_existing_matches(df, output_path)
    combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved matched jobs to: {output_path}")
    print(f"New matched jobs added: {new_count}")
    print(f"Total unique matched jobs: {len(combined_df)}")
    return combined_df


def main():
    print("Matching jobs with user profile...")
    matched_df = match_jobs()

    if matched_df.empty:
        print("No jobs to match.")
        return

    combined_df = save_matched_jobs(matched_df)
    print("\nTop matched jobs:")
    print(combined_df[["job_title", "company", "location", "match_score", "match_level"]].head(10))
    print("\nSkill matching completed successfully.")


if __name__ == "__main__":
    main()
