from pathlib import Path
from datetime import datetime

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRACKER_PATH = PROJECT_ROOT / "data" / "application_tracker.csv"
REPORT_PATH = PROJECT_ROOT / "output" / "daily_report.txt"


def load_tracker(path=TRACKER_PATH):
    if not path.exists():
        raise FileNotFoundError("application_tracker.csv not found. Run tracker.py first.")
    return pd.read_csv(path)


def safe_value(value):
    if pd.isna(value):
        return ""
    return value


def generate_report(tracker_df=None):
    tracker_df = tracker_df if tracker_df is not None else load_tracker()

    total_jobs = len(tracker_df)
    shortlisted = len(tracker_df[tracker_df["status"] == "Shortlisted"])
    saved_later = len(tracker_df[tracker_df["status"] == "Saved for Later"])
    ignored = len(tracker_df[tracker_df["status"] == "Ignored"])
    top_jobs = tracker_df.sort_values(by="ranking_score", ascending=False).head(10)

    missing_skill_counts = {}
    for skills in tracker_df.get("missing_skills", []):
        for skill in str(skills).split(","):
            skill = skill.strip()
            if skill:
                missing_skill_counts[skill] = missing_skill_counts.get(skill, 0) + 1

    top_missing_skills = sorted(missing_skill_counts.items(), key=lambda item: item[1], reverse=True)[:5]

    report_lines = [
        "=" * 60,
        "AI JOB AGENT - DAILY JOB REPORT",
        "=" * 60,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SUMMARY",
        "-" * 60,
        f"Total jobs tracked: {total_jobs}",
        f"Shortlisted jobs: {shortlisted}",
        f"Saved for later: {saved_later}",
        f"Ignored jobs: {ignored}",
        "",
        "BEST JOBS TO REVIEW",
        "-" * 60,
    ]

    if top_jobs.empty:
        report_lines.append("No jobs available today.")
    else:
        for rank, (_, job) in enumerate(top_jobs.iterrows(), start=1):
            report_lines.extend([
                f"{rank}. {safe_value(job.get('job_title', ''))}",
                f"   Company: {safe_value(job.get('company', ''))}",
                f"   Location: {safe_value(job.get('location', ''))}",
                f"   Ranking Score: {safe_value(job.get('ranking_score', ''))}%",
                f"   Recommendation: {safe_value(job.get('recommendation', ''))}",
                f"   Match Score: {safe_value(job.get('match_score', ''))}% ({safe_value(job.get('match_level', ''))})",
                f"   Status: {safe_value(job.get('status', ''))}",
                f"   Why: {safe_value(job.get('ranking_reason', ''))}",
                f"   Matched Skills: {safe_value(job.get('matched_skills', ''))}",
                f"   Missing Skills: {safe_value(job.get('missing_skills', ''))}",
                f"   URL: {safe_value(job.get('job_url', ''))}",
                "",
            ])

    report_lines.extend([
        "TOP MISSING SKILLS",
        "-" * 60,
    ])

    if top_missing_skills:
        for skill, count in top_missing_skills:
            report_lines.append(f"- {skill}: missing from {count} job(s)")
    else:
        report_lines.append("No missing skill signals found.")

    report_lines.extend([
        "",
        "RECOMMENDED ACTION",
        "-" * 60,
    ])

    if shortlisted > 0:
        report_lines.append(f"Review the {shortlisted} shortlisted job(s) first and mark approval_status as Approved or Rejected.")
    elif saved_later > 0:
        report_lines.append("No high-priority jobs today. Review saved jobs only if the role title and location look promising.")
    else:
        report_lines.append("No suitable jobs today. Run the collector again later or add another job source.")

    return "\n".join(report_lines)


def save_report(report_text, output_path=REPORT_PATH):
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_text)
    print(f"Daily report saved to: {output_path}")


def main():
    print("Generating daily job report...")
    report_text = generate_report()
    print("\n")
    print(report_text)
    save_report(report_text)
    print("\nReport generation completed successfully.")


if __name__ == "__main__":
    main()
