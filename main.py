"""
Monitor job openings in Europe using the official Adzuna API.

How it works (briefly):
1. Read search settings from config.yaml (country, job title, region, number of pages)
2. Go to Adzuna for each results page and request job openings
3. Parse the JSON response into flat strings (job title, company, salary, city, link, date)
4. Save everything in CSV and XLSX

No HTML parsing or security bypasses—we use the official,
documented, and free API, so the solution is legal and won't break
when the website layout changes.
"""

import logging
import os
import time
from datetime import date
from typing import Any

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

from send_email import send_email_with_attachments

load_dotenv()

logging.basicConfig(
    filename="logs/scraper.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
OUTPUT_DIR = "output"
LOGS_DIR = "logs"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# all events (requests, errors, results) are written to scraper.log —
# this is the "logging and monitoring module" from the specifications


def load_config(path: str = "config.yaml") -> dict[str, Any]:
    # We read the YAML config and turn it into a regular Python dictionary.
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_credentials() -> tuple[str | None, str | None]:
    """
    Load API credentials from the .env file (never hardcoded, never in config.yaml).
    Returns a (app_id, app_key) tuple, or (None, None) if missing.
    """
    load_dotenv()  # reads variables from a local .env file into the environment
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    return app_id, app_key


def fetch_page(
    config: dict | None = None,
    app_id: str = "",
    app_key: str = "",
    page_number: int = 0,
) -> dict | None:
    """
    Requests a single page of search results from Adzuna.
    page_number — page index, starting at 1.
    Returns the parsed JSON response, or None on failure.
    """
    if config is None:
        config = {}

    country = config["search"]["country"]
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page_number}"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": config["search"]["what"],
        "where": config["search"]["where"],
        "results_per_page": config["search"]["results_per_page"],
        "sort_by": config["search"]["sort_by"],
        "max_days_old": config["search"]["max_days_old"],
        "content-type": "application/json",
    }

    try:
        # timeout=15 — don't wait longer than 15 seconds, otherwise treat as a failure
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()  # raises an exception on a 4xx/5xx response
        return resp.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching page {page_number}: {e}")
        print(f"Error on page {page_number}: {e}")
        return None


def parse_results(raw_json: dict | None) -> list:
    """
    Turns Adzuna's JSON response into a list of flat dictionaries −
    one for each vacancy.
    """
    items: list = []
    if not raw_json or "results" not in raw_json:
        return items

    for job in raw_json["results"]:
        # We safely retrieve nested fields using .get() to avoid crashes,
        # if Adzuna didn't send a field for a specific vacancy
        company = job.get("company", {}).get("display_name")
        location = job.get("location", {}).get("display_name")
        category = job.get("category", {}).get("label")

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        items.append(
            {
                "Title": job.get("title"),
                "Company": company,
                "Location": location,
                "Category": category,
                "Salary From": salary_min,
                "Salary Up": salary_max,
                "Employment Type": job.get("contract_time"),
                "Publish Date": job.get("created"),
                "Link": job.get("redirect_url"),
            }
        )
    return items


def scrape_all(
    config: dict | None = None,
    app_id: str = "",
    app_key: str = "",
) -> list:
    """Walks through all pages up to max_pages and collects every vacancy into one list."""
    if config is None:
        config = {}

    all_items: list = []

    max_pages = config["search"]["max_pages"]

    for page in range(1, max_pages + 1):
        raw = fetch_page(config, app_id, app_key, page)
        if raw is None:
            continue  # this page failed to load — skip it, don't abort the whole run

        items = parse_results(raw)
        if not items:
            logging.info(f"Page {page}: no vacancies found, stopping")
            print(f"Page {page}: empty, no more vacancies")
            break

        all_items.extend(items)
        logging.info(f"Page {page}: got {len(items)} vacancies")
        print(f"Page {page}: {len(items)} vacancies")

        time.sleep(1)  # polite pause between requests to the API

    return all_items


def export(items: list[Any] | None = None, filename_base: str = "vacancies_result") -> None:
    """Saves collected job postings to CSV and XLSX with auto-width columns."""
    if not items:
        print("There is no data to save.")
        return

    df = pd.DataFrame(items)
    df["Collection date"] = date.today().isoformat()

    csv_path = os.path.join(OUTPUT_DIR, f"{filename_base}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    xlsx_path = os.path.join(OUTPUT_DIR, f"{filename_base}.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="vacancies")
        worksheet = writer.sheets["vacancies"]
        for i, col in enumerate(df.columns):
            width = max(df[col].fillna("").astype(str).map(len).max(), len(str(col))) + 2
            worksheet.column_dimensions[chr(65 + i)].width = min(width, 60)


if __name__ == "__main__":
    config = load_config()
    app_id, app_key = load_credentials()
    if not app_id or not app_key or app_id != app_id:
        print(
            "Missing API credentials. Copy .env.example to .env and fill in your "
            "real app_id / app_key — get them for free at "
            "https://developer.adzuna.com/signup"
        )
    else:
        filename_base = config["output"]["filename_base"]
        items = scrape_all(config, app_id, app_key)
        export(items, filename_base)
        print(f"Done: {len(items)} vacancies saved to " f"{filename_base}.csv / .xlsx")
        recipient = os.getenv("RECIPIENT_EMAIL")
        if recipient and items:
            print("\nPreparing to send mail...")
            send_email_with_attachments(filename_base, recipient)
        elif not recipient:
            print("\nRECIPIENT_EMAIL not set in .env. Skipping sending the email.")
