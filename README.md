# European Job Monitoring (Adzuna API)

Collects job postings from the Adzuna job board (a job aggregator operating in 10+ European countries: Germany, the UK, France, Poland, Spain, Italy, and others) and saves them in Excel and CSV formats.

Uses the official, free, and documented API – no HTML scraping. This means it doesn't violate terms of use, won't break when the layout changes, and doesn't require a proxy or CAPTCHA bypass.

## 1. Installing Keys (One-Time)

1. Register at https://developer.adzuna.com/signup (free, no moderation)
2. Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
3. Open `.env` and enter your keys:
```
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

The `.env` file contains secrets and should never be shared with third parties or placed in Git – it is already added to `.gitignore`.

## 4. Configuring email delivery of results (optional)

If you want the completed job posting file to be automatically emailed to the client after each run, add the following block to .env (next to the Adzuna keys):

```bash
# SMTP settings (default for Gmail)
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=465
SMTP_USER="your_email@gmail.com"

# IMPORTANT: This must be a special "Application Password," not a regular password!
SMTP_PASSWORD="app_password"

# Client email (where to send files)
RECIPIENT_EMAIL="client_email@example.com"
```

**How ​​to get the `SMTP_PASSWORD` (app password) for Gmail:**

1. Go to https://myaccount.google.com/security
2. Enable two-factor authentication (2-Step Verification) if it isn't already enabled — without it, the option below won't appear.
3. Go to https://myaccount.google.com/apppasswords
4. In the "App name" field, enter any name, for example, `vacancy-scraper`
5. Click **Create** — Google will display a 16-character password in the format `abcd efgh ijkl mnop`
6. Enter it in `.env` **without spaces**: `abcdefghijklmnop`
(password) It's only shown once—copy it immediately.
Your regular Gmail password won't work for this—Google blocks third-party programs from logging in with it.

## 5. Launching the program

You don't need to install anything manually—the launch scripts automatically create the environment and install dependencies on the first run.

**Windows:**
Double-click `run.bat` (or run from the command line).

**macOS / Linux:**
```bash
chmod +x run.sh # once, allow running
./run.sh
```

It will take a little longer the first time you run it (dependencies are installed), but it's faster on subsequent runs.

## 6. Search settings

In `config.yaml` (no code, no keys—only search parameters):

| Parameter | What does it mean |
|---|---|
| `country` | Country code: `gb`, `de`, `fr`, `pl`, `es`, `it`, `nl`, `at`, etc. |
| `what` | job title / keywords |
| `where` | city (blank — entire country) |
| `max_pages` | how many pages to crawl (50 vacancies per page) |
| `max_days_old` | do not show vacancies older than N days |

## 7. Result

After running, the following will appear in the folder:
- `vacancies_result.csv`
- `vacancies_result.xlsx`
- `scraper.log` — the run log
## 8. Regular Run (Optional)

**macOS/Linux (cron):**
```bash
0 9 * * * cd /path/to/project && ./run.sh
```

**Windows (Task Scheduler):** Create a task that runs `run.bat` once a day.

## Project File Structure

| File | Purpose | Contains secrets? |
|---|---|---|
| `main.py` | Data collection and export logic | None |
| `config.yaml` | Search settings | None |
| `.env` | API keys + SMTP email settings (created by you from `.env.example`) | **Yes** |
| `.env.example` | Template for `.env` | No |
| `run.sh` / `run.bat` | One-command/click launch | No |
| `requirements.txt` | Python dependencies list | No |

## Support

If Adzuna changes the API response format, you will need to edit `parse_results()` in `main.py`. Changing countries/job titles does not require any code changes—everything can be changed through `config.yaml`.