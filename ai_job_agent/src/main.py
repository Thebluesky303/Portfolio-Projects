from job_collector import collect_jobs
from job_ranker import rank_jobs, save_ranked_jobs
from report_generator import generate_report, save_report
from skill_matcher import match_jobs, save_matched_jobs
from tracker import create_application_tracker, save_tracker


def main():
    print("\nStarting AI Job Agent Pipeline...\n")

    raw_jobs = collect_jobs()
    if raw_jobs.empty:
        print("Pipeline stopped because no relevant jobs were available.")
        return

    matched_jobs = match_jobs(raw_jobs)
    if matched_jobs.empty:
        print("Pipeline stopped because no jobs could be matched.")
        return
    matched_jobs = save_matched_jobs(matched_jobs)

    ranked_jobs = rank_jobs(matched_jobs)
    if ranked_jobs.empty:
        print("Pipeline stopped because no jobs could be ranked.")
        return
    ranked_jobs = save_ranked_jobs(ranked_jobs)

    tracker = create_application_tracker(ranked_jobs)
    tracker = save_tracker(tracker)

    report_text = generate_report(tracker)
    save_report(report_text)

    print("\nAI Job Agent Pipeline Completed Successfully.")


if __name__ == "__main__":
    main()
