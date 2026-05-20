import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = PROJECT_ROOT / "config" / "user_profile.json"
MATCHED_JOBS_PATH = PROJECT_ROOT / "data" / "matched_jobs.csv"
RANKED_JOBS_PATH = PROJECT_ROOT / "data" / "ranked_jobs.csv"


ROLE_WEIGHTS = {
    "title": 30,
    "skills": 25,
    "location": 15,
    "experience": 15,
    "remote": 5,
    "project": 10,
}


NEGATIVE_TITLE_TERMS = [
    "senior",
    "lead",
    "principal",
    "manager",
    "head of",
    "director",
    "recruiter",
    "recruitment",
    "marketing",
    "sales",
]


def load_user_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_matched_jobs(path=MATCHED_JOBS_PATH):
    if not path.exists():
        raise FileNotFoundError("matched_jobs.csv not found. Run skill_matcher.py first.")
    return pd.read_csv(path)


def split_csv_text(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def text_contains_any(text, terms):
    normalized = str(text or "").lower()
    return any(str(term).lower() in normalized for term in terms)


def calculate_title_score(title, job_text, profile):
    target_roles = profile.get("target_roles", [])
    exact_match = text_contains_any(title, target_roles)
    broad_title_match = text_contains_any(title, [
        "data",
        "analyst",
        "analytics",
        "bi",
        "sql",
        "machine learning",
        "research",
        "reporting",
    ])
    weak_context_match = text_contains_any(title, ["ai"]) and text_contains_any(job_text, profile.get("skills", []))

    if exact_match:
        return ROLE_WEIGHTS["title"]
    if broad_title_match:
        return ROLE_WEIGHTS["title"] * 0.65
    if weak_context_match:
        return ROLE_WEIGHTS["title"] * 0.35
    return 0


def calculate_skill_score(row, profile):
    total_skills = len(profile.get("skills", []))
    matched_skills = split_csv_text(row.get("matched_skills", ""))

    if total_skills == 0:
        return 0

    ratio = min(len(matched_skills) / total_skills, 1)
    return ROLE_WEIGHTS["skills"] * ratio


def calculate_location_score(job_text, profile):
    target_locations = profile.get("target_locations", [])
    if text_contains_any(job_text, target_locations):
        return ROLE_WEIGHTS["location"]
    if text_contains_any(job_text, [profile.get("target_country", "")]):
        return ROLE_WEIGHTS["location"] * 0.8
    return 0


def calculate_experience_score(job_text, profile):
    if text_contains_any(job_text, profile.get("experience_level", [])):
        return ROLE_WEIGHTS["experience"]
    if not text_contains_any(job_text, NEGATIVE_TITLE_TERMS):
        return ROLE_WEIGHTS["experience"] * 0.55
    return 0


def calculate_remote_score(row, job_text):
    if row.get("remote", False) is True or text_contains_any(job_text, ["remote", "hybrid"]):
        return ROLE_WEIGHTS["remote"]
    return 0


def calculate_project_score(job_text, profile):
    projects = profile.get("projects", [])
    project_skills = []
    for project in projects:
        project_skills.extend(project.get("skills", []))

    if not project_skills:
        return 0

    matched = sum(1 for skill in set(project_skills) if str(skill).lower() in str(job_text).lower())
    return ROLE_WEIGHTS["project"] * min(matched / 5, 1)


def calculate_penalty(row, profile, job_text):
    title = str(row.get("job_title", "")).lower()
    avoid_keywords = profile.get("avoid_keywords", [])
    penalty = 0
    reasons = []

    for keyword in avoid_keywords:
        if str(keyword).lower() in title:
            penalty += 30
            reasons.append(f"title includes '{keyword}'")
        elif str(keyword).lower() in str(job_text).lower():
            penalty += 12
            reasons.append(f"description includes '{keyword}'")

    for term in NEGATIVE_TITLE_TERMS:
        if term in title:
            penalty += 20
            reasons.append(f"title includes '{term}'")

    return min(penalty, 60), reasons


def classify_priority(score):
    if score >= 80:
        return "Apply First"
    if score >= 65:
        return "Strong Review"
    if score >= 50:
        return "Review Later"
    if score >= 35:
        return "Low Priority"
    return "Skip"


def build_reason(row, score_parts, penalty_reasons):
    positives = []
    if score_parts["title"] >= ROLE_WEIGHTS["title"] * 0.65:
        positives.append("role/title looks relevant")
    if score_parts["skills"] >= ROLE_WEIGHTS["skills"] * 0.25:
        positives.append("some profile skills match")
    if score_parts["location"] > 0:
        positives.append("location preference matches")
    if score_parts["experience"] > 0:
        positives.append("experience level looks suitable")
    if score_parts["remote"] > 0:
        positives.append("remote/hybrid friendly")
    if score_parts["project"] > 0:
        positives.append("connects to portfolio project skills")

    if penalty_reasons:
        positives.append("penalty: " + "; ".join(dict.fromkeys(penalty_reasons)))

    return "; ".join(positives) if positives else "limited match signals found"


def rank_jobs(matched_df=None):
    profile = load_user_profile()
    matched_df = matched_df if matched_df is not None else load_matched_jobs()

    ranked_rows = []
    for _, row in matched_df.iterrows():
        job_text = " ".join(str(row.get(column, "")) for column in [
            "job_title", "company", "location", "tags", "job_types", "description", "matched_skills"
        ])

        score_parts = {
            "title": calculate_title_score(row.get("job_title", ""), job_text, profile),
            "skills": calculate_skill_score(row, profile),
            "location": calculate_location_score(job_text, profile),
            "experience": calculate_experience_score(job_text, profile),
            "remote": calculate_remote_score(row, job_text),
            "project": calculate_project_score(job_text, profile),
        }
        penalty, penalty_reasons = calculate_penalty(row, profile, job_text)
        ranking_score = max(0, round(sum(score_parts.values()) - penalty, 2))

        ranked_row = row.to_dict()
        ranked_row.update({
            "ranking_score": ranking_score,
            "ranking_level": classify_priority(ranking_score),
            "recommendation": classify_priority(ranking_score),
            "ranking_reason": build_reason(row, score_parts, penalty_reasons),
        })
        ranked_rows.append(ranked_row)

    ranked_df = pd.DataFrame(ranked_rows)
    if not ranked_df.empty:
        ranked_df = ranked_df.drop_duplicates(subset=["job_url"], keep="first")
        ranked_df = ranked_df.sort_values(by=["ranking_score", "match_score"], ascending=False)
    return ranked_df


def merge_with_existing_rankings(new_df, output_path=RANKED_JOBS_PATH):
    if new_df.empty:
        return new_df, 0

    if not output_path.exists():
        return new_df.drop_duplicates(subset=["job_url"], keep="first"), len(new_df)

    existing_df = pd.read_csv(output_path)
    existing_urls = set(existing_df.get("job_url", pd.Series(dtype=str)).fillna("").astype(str))
    new_only_df = new_df[~new_df["job_url"].fillna("").astype(str).isin(existing_urls)]
    combined_df = pd.concat([existing_df, new_only_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["job_url"], keep="first")
    combined_df = combined_df.sort_values(by=["ranking_score", "match_score"], ascending=False)
    return combined_df, len(new_only_df)


def save_ranked_jobs(df, output_path=RANKED_JOBS_PATH):
    output_path.parent.mkdir(exist_ok=True)
    combined_df, new_count = merge_with_existing_rankings(df, output_path)
    combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved ranked jobs to: {output_path}")
    print(f"New ranked jobs added: {new_count}")
    print(f"Total unique ranked jobs: {len(combined_df)}")
    return combined_df


def main():
    print("Ranking matched jobs...")
    ranked_df = rank_jobs()

    if ranked_df.empty:
        print("No jobs to rank.")
        return

    combined_df = save_ranked_jobs(ranked_df)
    print("\nTop ranked jobs:")
    print(combined_df[["job_title", "company", "location", "ranking_score", "recommendation"]].head(10))
    print("\nJob ranking completed successfully.")


if __name__ == "__main__":
    main()

