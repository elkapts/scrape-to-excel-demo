#1/bin/bash
# Running the project on macOS / Linux.
# Double-clicking isn't possible—run it via terminal:
# chmod +x run.sh (once to allow running)
# ./run.sh

set -e

cd "$(dirname "$0")" 


if [ ! -d "venv" ]; then
    echo "Creating a virtual environment (venv)..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Checking dependencies..."

pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo ""
    echo "The .env file was not found."
    echo "1) Copy the example: cp .env.example .env"
    echo "2) Enter your keys from https://developer.adzuna.com/signup"
    echo ""
    exit 1
fi

echo "Starting job posting..."

python main.py

echo ""
echo "Done. The results are in the vacancies_result.csv / .xlsx files in this folder. Send to Gmail."
