# AI Job Agent

A Python job-search assistant that collects job listings, filters them against a personal profile, matches required skills, ranks opportunities, and generates an application tracker plus a daily review report.

## Why This Project Exists

Searching for entry-level data, analytics, AI, and machine-learning roles can be noisy. This project automates the first screening step so the best jobs are easier to review first.

The agent is configured for Bikash Limbu's UK-focused job search profile, but the profile can be edited for any user.

## Features

- Fetches live jobs from the Arbeitnow job API
- Filters out unsuitable roles using title, location, skills, experience level, and avoid keywords
- Matches job descriptions against the user's skills
- Ranks jobs with a weighted scoring model
- Creates a CSV application tracker
- Generates a plain-text daily job report
- Keeps private/generated files out of Git with `.gitignore`

## Project Structure

```text
ai_job_agent/
  config/
    user_profile.json
  data/
    raw_jobs.csv
    matched_jobs.csv
    ranked_jobs.csv
    application_tracker.csv
  output/
    daily_report.txt
  src/
    job_collector.py
    skill_matcher.py
    job_ranker.py
    tracker.py
    report_generator.py
    main.py
  README.md
  requirements.txt
  .gitignore
```

## How The Pipeline Works

1. `job_collector.py` fetches jobs and applies strict first-pass filtering.
2. `skill_matcher.py` compares each job with the skills in `config/user_profile.json`.
3. `job_ranker.py` calculates a final ranking score using title, skills, location, experience, remote/hybrid fit, project relevance, and penalties.
4. `tracker.py` creates an application tracker with review statuses.
5. `report_generator.py` writes a readable daily report to `output/daily_report.txt`.
6. `main.py` runs the full pipeline.

## Ranking Logic

The ranking score uses these signals:

- Role/title relevance
- Skill match percentage
- Target location match
- Entry-level, graduate, junior, intern, or research suitability
- Remote/hybrid bonus
- Portfolio project skill overlap
- Penalty for senior, lead, manager, recruiter, sales, or other unwanted keywords

Recommendations are grouped as:

- `Apply First`
- `Strong Review`
- `Review Later`
- `Low Priority`
- `Skip`

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Project

From the project root:

```bash
python src/main.py
```

Or run steps individually:

```bash
python src/job_collector.py
python src/skill_matcher.py
python src/job_ranker.py
python src/tracker.py
python src/report_generator.py
```


## Repeat Runs And Saved Data

The CSV files in `data/` are cumulative. When you run the pipeline again, the program checks existing `job_url` values and only appends jobs that are new.

These files keep old jobs and avoid duplicate job URLs:

- `data/raw_jobs.csv`
- `data/matched_jobs.csv`
- `data/ranked_jobs.csv`
- `data/application_tracker.csv`

The daily report is intentionally refreshed each run:

- `output/daily_report.txt`

Manual tracker fields such as `status`, `approval_status`, `applied_date`, and `notes` are preserved for jobs that already exist in `application_tracker.csv`.
## Outputs

The pipeline creates:

- `data/raw_jobs.csv`: filtered collected jobs
- `data/matched_jobs.csv`: jobs with skill matches
- `data/ranked_jobs.csv`: jobs with final ranking scores and recommendations
- `data/application_tracker.csv`: review/apply tracking sheet
- `output/daily_report.txt`: human-readable summary report

## Customize The Profile

Edit:

```text
config/user_profile.json
```

You can update:

- target roles
- locations
- skills
- experience level
- avoid keywords
- portfolio projects
- match thresholds

## Current Limitations

- Uses one job source only
- Keyword-based matching does not fully understand context
- Live API results vary day to day
- No email or notification integration yet
- No automated application submission, by design

## Future Improvements

- Add more job sources such as Remotive, Reed, Adzuna, or manually exported LinkedIn CSV files
- Add semantic matching with embeddings
- Add unit tests
- Add an HTML dashboard or Streamlit interface
- Add scheduled daily runs
- Add email summaries

