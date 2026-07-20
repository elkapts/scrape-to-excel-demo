# European Job Vacancy Monitor - Client Guide

## What this is

The program automatically collects up-to-date job vacancies matching your criteria (job title, country, city) from a major European job board and delivers a ready-to-use table - Excel and CSV - with job title, company, location, salary, and a link to each listing.

Data is collected through an **official data source**, not by scraping the website - so the service doesn't violate anyone's terms of use and won't suddenly break due to a block.

## What you get

After each run - two files with the same data (pick whichever is easier to open):

| File | Open with |
|---|---|
| `output/vacancies_result.xlsx` | Microsoft Excel, Google Sheets, LibreOffice |
| `output/vacancies_result.csv` | Excel, Google Sheets, any text editor |

**Table columns:**

| Title | Company | Location | Category | Salary From | Salary To | Contract Type | Date Posted | Link | Date Collected |
|---|---|---|---|---|---|---|---|---|---|

## How to run it

<!-- **On Windows:** double-click `run.bat` -->
**On Mac:** open Terminal in the project folder and type `./run.sh`

Within 10-60 seconds (depending on how many vacancies are found), the result files will appear in the same folder.

## How often can you run it

As often as you like - the data source updates continuously. If you'd like collection to happen automatically on a schedule (e.g., every morning) without you doing anything, that can be set up separately - just ask.

## If something goes wrong

- The program won't start / shows an error - take a screenshot of the message and send it over
- `scraper.log` in the project folder is the log of the last run - you can attach it too when asking for help
- The table comes out empty - the search may be too narrow (a rare job title + a small city); try broadening the criteria or reach out for help

## Quality assurance

The program is covered by an automated test suite (13 tests, 83% of the code verified) that runs on every code update, ensuring data collection and saving keep working correctly and don't break with future changes. Details are in the technical specification, section "Quality Assurance."

## Support

For configuration changes (job title, country, adding email notifications) - contact the developer. All search parameters are changed in a single file (`config.yaml`) with no need to touch the program's code.