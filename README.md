![Tests](https://github.com/elkapts/scrape-to-excel-demo/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)

# European Job Vacancy Monitor (Adzuna API)

Collects vacancies from **Adzuna** (a job aggregator covering 10+ European countries: Germany, UK, France, Poland, Spain, Italy, and more) and saves them to Excel and CSV.

Uses the **official, free, documented API** - not HTML scraping. This means it doesn't violate any terms of service, doesn't break when the site's markup changes, and needs no proxies or CAPTCHA bypassing.

**Requirements:** Python 3.11+. Tested on Python 3.13 and 3.14 (stable). Python 3.15 is currently in beta (final release expected October 2026) - the code uses no version-specific features, so it should keep working once 3.15 ships, but treat it as untested until then.

## 1. Set up your API keys (one-time)

1. Sign up at https://developer.adzuna.com/signup (free, no approval wait)
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your keys:
   ```
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```

The `.env` file contains secrets and must never be shared or committed to Git - it's already listed in `.gitignore`.

## 2. Email delivery of results (optional)

To have the result file emailed automatically after each run, add this block to `.env` (next to the Adzuna keys):

```bash
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=465
SMTP_USER="your_email@gmail.com"
SMTP_PASSWORD="your_app_password"   # a Gmail "App Password", not your regular password
RECIPIENT_EMAIL="client_email@example.com"
```

To generate a Gmail App Password: enable 2-Step Verification at https://myaccount.google.com/security, then create one at https://myaccount.google.com/apppasswords.

## 3. Run the program

No manual setup needed - the launch scripts create the environment and install dependencies on first run.

**Windows:**
Double-click `run.bat` (or run it from the command line).

**macOS / Linux:**
```bash
chmod +x run.sh   # once, to allow running
./run.sh
```

The first run takes a bit longer (installing dependencies); later runs are faster.

## 4. Search settings

In `config.yaml` (no code, no keys - just search parameters):

| Parameter | Meaning |
|---|---|
| `country` | Adzuna country code: `gb`, `de`, `fr`, `pl`, `es`, `it`, `nl`, `at`, etc. |
| `what` | job title / keywords |
| `where` | city (leave empty to search the whole country) |
| `max_pages` | how many pages to walk through (50 vacancies per page) |
| `max_days_old` | exclude vacancies older than N days |

## 5. Output

After running, you'll find in the project folder:
- `output/vacancies_result.csv`
- `output/vacancies_result.xlsx`
- `logs/scraper.log` - run log

## 6. Interactive dashboard (optional)

For a visual, filterable view of the collected data instead of opening the
spreadsheet directly:

```bash
streamlit run dashboard.py
```

This opens a browser tab with:
- Keyword search (title/company), location, contract type, and salary range filters
- Summary metrics (vacancy count, unique companies/locations, average salary)
- Charts: vacancies by location, salary distribution
- A sortable table with clickable links to each listing, and a "download filtered results" button

The dashboard only reads `output/vacancies_result.csv` - it never calls the
Adzuna API itself. Run `main.py` (via `run.sh`/`run.bat`) first to generate
or refresh the data; the dashboard picks up the latest file automatically.

## 7. Deploy the dashboard for a client (Streamlit Community Cloud)

To give a client a permanent link they can open in any browser, without
installing anything, deploy the dashboard to [Streamlit Community
Cloud](https://streamlit.io/cloud) (free):

1. Push this repo to GitHub (public, or grant Streamlit access if private).
2. Go to https://share.streamlit.io, sign in with GitHub, click **"New app"**.
3. Select this repository, branch `main`, and set the main file to `dashboard.py`.
4. Deploy. Streamlit installs `requirements.txt` automatically.

You'll get a URL like `https://your-app-name.streamlit.app` to share directly.

**Keeping the data fresh automatically:** Streamlit Cloud only runs
`dashboard.py` - it does not run `main.py` on its own. This repo includes
`.github/workflows/refresh-data.yml`, a scheduled GitHub Action that runs
`main.py` once a day and commits the updated `output/vacancies_result.csv`
back to the repo. Streamlit Cloud detects the change and reloads the
dashboard automatically - no manual steps needed after initial setup.

To enable it, add your Adzuna keys as **repository secrets** (not to a
committed file): on GitHub, go to **Settings → Secrets and variables →
Actions → New repository secret**, and add `ADZUNA_APP_ID` and
`ADZUNA_APP_KEY`. You can also trigger it manually any time from the
**Actions** tab (useful right after changing `config.yaml`).

## 8. Scheduled runs on your own machine (optional)

**macOS/Linux (cron):**
```bash
0 9 * * * cd /path/to/project && ./run.sh
```

**Windows (Task Scheduler):** create a daily task that runs `run.bat`.

## 9. QA / Testing

The project ships with an automated test suite (`tests/test_main.py` +
`tests/test_dashboard.py`, 16 tests, 89% combined coverage of `main.py` and
`dashboard.py`) that runs automatically via GitHub Actions on every push
(see `.github/workflows/ci.yml`). No real API calls are made in tests - all
network calls are mocked, and the dashboard tests use Streamlit's official
`AppTest` framework instead of a real browser.

Run tests locally:
```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=main --cov=dashboard
```

## Project structure

| File | Purpose | Contains secrets? |
|---|---|---|
| `main.py` | Data collection and export logic | No |
| `dashboard.py` | Interactive Streamlit dashboard (read-only viewer) | No |
| `config.yaml` | Search settings | No |
| `.env` | API keys + SMTP settings (created by you from `.env.example`) | **Yes** |
| `.env.example` | Template for `.env` | No |
| `run.sh` / `run.bat` | One-command/one-click launch | No |
| `requirements.txt` | Production dependencies | No |
| `requirements-dev.txt` | Testing dependencies | No |
| `tests/test_main.py` | Automated test suite for main.py | No |
| `tests/test_dashboard.py` | Automated test suite for dashboard.py | No |
| `.github/workflows/ci.yml` | CI pipeline configuration | No |

## Maintenance

If Adzuna changes its API response format, `parse_results()` in `main.py` will need updating. Changing countries/job titles requires no code changes - everything is controlled via `config.yaml`.