![Tests](https://github.com/elkapts/scrape-to-excel-demo/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)

## Why I built this

A freelance client needed ongoing visibility into European job market data
without relying on fragile HTML scraping that breaks on every site redesign
or violates a platform's terms of service. This project uses an official,
documented API instead — the same result (a clean spreadsheet), delivered
in a way that keeps working and stays on the right side of the source's
usage policy.

## What it looks like

![Result preview](docs/ScreenRecording2026-07-20at14.05.08-ezgif.com-video-to-gif-converter.gif)

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
- `vacancies_result.csv`
- `vacancies_result.xlsx`
- `scraper.log` - run log

## 6. Scheduled runs (optional)

**macOS/Linux (cron):**
```bash
0 9 * * * cd /path/to/project && ./run.sh
```

**Windows (Task Scheduler):** create a daily task that runs `run.bat`.

## 7. QA / Testing

The project ships with an automated test suite (`tests/test_main.py`, 13 tests, 83% coverage of `main.py`) that runs automatically via GitHub Actions on every push (see `.github/workflows/ci.yml`). No real API calls are made in tests - all network calls are mocked.

Run tests locally:
```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=main
```

## Project structure

| File | Purpose | Contains secrets? |
|---|---|---|
| `main.py` | Data collection and export logic | No |
| `config.yaml` | Search settings | No |
| `.env` | API keys + SMTP settings (created by you from `.env.example`) | **Yes** |
| `.env.example` | Template for `.env` | No |
| `run.sh` / `run.bat` | One-command/one-click launch | No |
| `requirements.txt` | Production dependencies | No |
| `requirements-dev.txt` | Testing dependencies | No |
| `tests/test_main.py` | Automated test suite | No |
| `.github/workflows/ci.yml` | CI pipeline configuration | No |

## Maintenance

If Adzuna changes its API response format, `parse_results()` in `main.py` will need updating. Changing countries/job titles requires no code changes - everything is controlled via `config.yaml`.
