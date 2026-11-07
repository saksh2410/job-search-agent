# Saksham's job search agent

A local Python agent that finds individual job listings, filters them against your profile, and produces a ranked shortlist with evidence and review flags. Python 3.11+; no pip packages needed.

## Start on your Windows laptop

1. Extract this ZIP and open the folder in VS Code.
2. In the VS Code PowerShell terminal, test without API usage:

```powershell
python agent.py demo --out demo-output
```

Open `demo-output/report.html`. These are clearly marked synthetic examples, not vacancies.

3. Set your existing OpenAI API key in your own terminal (do not send it in chat):

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
python agent.py run --region Singapore
```

4. Open `output/report.html` for the shortlist, or `output/shortlist.csv` in Excel. A browser report does not require a web server.

On macOS/Linux, use `export OPENAI_API_KEY="YOUR_API_KEY"` instead.

## What it searches

| Source | Access method | Coverage limits |
|---|---|---|
| Company career pages | OpenAI web search, plus direct Greenhouse/Lever public feeds for configured companies | Search coverage varies. Direct feeds reflect published jobs at retrieval time. |
| LinkedIn | Web search restricted to linkedin.com | Publicly discoverable individual job URLs only; no authenticated account or complete inventory. |
| Indeed | Web search restricted to indeed.com | Indexed job leads only; no complete inventory. |
| Naukri | Web search restricted to naukri.com | Indexed job leads only; no complete inventory. |

The agent does not log in or scrape protected pages. Job-alert content and manually researched listings can also be imported as JSON. No applications or messages are sent.

Search output URLs must occur in the API's search sources/citations. This checks URL provenance, not every extracted claim. Search-derived requirements remain unverified and are marked for review. Direct feed listings use the full available job description. A source error appears in the report and produces exit code 2, rather than silently reporting complete coverage.

## Your initial filters

- AI/ML Engineer, applied GenAI/LLM, MLOps, applied scientist, data scientist, and selective quantitative roles.
- Singapore, UAE, Australia, selected European countries/cities, and India.
- Roughly two years' experience; a permissive maximum of four years explicitly required allows stretch roles.
- Principal, staff, lead, management and internship titles excluded. Senior titles remain eligible if requirements fit.
- Python, SQL, Azure, OpenAI, Docker, Kubernetes, pytest and your credit-risk background contribute to ranking.
- Banks, fintech and selected technology companies are preferences, not exclusive requirements.
- Overseas work authorization is flagged for review; unknown sponsorship is never treated as confirmed.

Edit `config.json` to change these choices. `allowed_companies` is an exact, case-insensitive allowlist; an empty list means all companies. `excluded_companies` blocks exact names. `preferred_companies` adds a small ranking bonus. Add naming variants if a company uses multiple legal names.

Country/city aliases are explicit. Add cities/countries to `profile.regions` to expand coverage; unknown named locations go to the rejection audit. Unknown locations and remote eligibility remain review leads. The experience parser handles common formats, not every phrasing, and may flag requirements for review. Fit scores are transparent keyword overlap, not a hiring probability or a claim about company quality.

## Commands

```powershell
# All four discovery sources in one specified region (up to four API requests)
python agent.py run --region UAE

# One source, smaller paid test
python agent.py run --region India --source naukri --max-calls 1

# Rotates through one region each run, using persisted rotation.json
python agent.py run

# Configured public company feeds only; no OpenAI key needed
python agent.py run --ats-only

# Import alert/manual research data, plus company feeds, without paid discovery
python agent.py run --ats-only --import-file my-listings.json

# Keep application status in the tracker (copy ID from CSV/report)
python agent.py status --id JOB_ID --value applied

# Run offline tests
python -m unittest discover -s tests -v
```

By default a search visits one region per run. It does not exhaustively search every country in Europe, every company or every role. A run targets at most eight results per discovery call, plus all configured career-board jobs. Change `jobs_per_call` and `max_output_tokens` together if increasing volume.

`max-calls` caps discovery requests, not dollars or the number of internal web searches; transient HTTP retries may add requests. API usage is separate from your ChatGPT subscription. The audit records API usage returned by the service. Set project spending controls yourself before regular use; costs depend on model, tokens and search usage.

## Add company career-board feeds

Two starter Greenhouse boards are configured: Stripe and Databricks. Change or remove them as desired; these are example targets, not an assertion that every role is appropriate.

A company using Greenhouse has a board token, often visible in its hosted career URL. For Lever, use the site slug. Add entries to `career_boards`:

```json
[
  {"provider": "greenhouse", "slug": "ACTUAL_BOARD_TOKEN", "company": "Actual Company"},
  {"provider": "lever", "slug": "ACTUAL_SITE_SLUG", "company": "Actual Company", "region": "global"}
]
```

Use `"region":"eu"` for Lever's EU API. Slugs must be confirmed from the company's actual careers page; do not assume all employer names are valid tokens. Other career platforms are searched through web search; a generic Workday scraper is not included.

## Import format

```json
{"jobs":[{
  "title":"Machine Learning Engineer",
  "company":"Actual Company",
  "url":"https://company.example/jobs/123",
  "location":"Singapore",
  "description":"Paste real requirements here",
  "source":"manual",
  "posted_at":"",
  "work_authorization":"",
  "requisition_id":""
}]}
```

## Outputs and persistence

- `report.html`: this run's ranked matches, links, skills, source confidence, and eligibility flags.
- `shortlist.csv`: this run's matches, compatible with Excel; safe escaping of formula-like cells.
- `audit.json`: all candidates, including rejections with reasons, source errors, and search usage.
- `tracker.sqlite3`: persistent first/last seen dates and application statuses.
- `rotation.json`: next region for unspecified-region runs.

Reports show current-run findings, not the entire historical tracker. Missing jobs are not automatically marked closed: absence from search does not prove closure. URLs and explicit company/requisition IDs are deduplicated. Cross-source duplicates without matching URLs or requisition IDs may remain, which avoids merging different jobs with identical titles. Application status stays intact for the same canonical URL; employer/platform link changes may create a new record.

Keep your output folder between runs. Demo output has a separate folder in the recommended command. API keys are read from the environment and are never saved in configuration or reports.

## Run daily on Windows (optional, not installed by this package)

In Task Scheduler, create a daily task with `python.exe` as the program, absolute arguments such as `C:\path\job-search-agent\agent.py run`, and the project directory as **Start in**. A temporary `$env:` variable only exists in your current terminal; the scheduled process needs its own user environment variable or secret-loading wrapper. The computer must be awake and connected. Running manually is recommended before enabling a schedule. No daily automation is activated by downloading this package.

## Validation and limits

Offline tests cover experience/title/location/company filters, evidence provenance, duplicate handling, status persistence, CSV/URL safety, and Greenhouse mapping. A live test on 4 October 2026 fetched 1,603 listings from the configured Stripe and Databricks boards and shortlisted three with the initial filters. The included `live-sample/report.html` and `live-sample/shortlist.csv` capture that test; these roles still need manual eligibility review. Paid OpenAI discovery cannot be verified here without your API credentials. This package is a working first version with heuristic filtering, not a guarantee of complete job-board coverage.

Primary implementation references:
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://docs.greenhouse.io/job-board.html
- https://github.com/lever/postings-api
