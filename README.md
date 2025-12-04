RTO Automated Scraper & Data Pipeline

This repository automates:

Scraping daily Vahan RTO Maker × Fuel Excel sheets using Selenium

Renaming + structuring the downloaded files

Consolidating into a single daily CSV

Computing delta sheets between yesterday vs today

Appending results into a master Excel file

The system handles browser crashes, 503 errors, auto-restart, parallel multiprocessing, and logging per state.

🚀 Features

Parallel scraping for:

Karnataka

Tamil Nadu

Kerala

Puducherry

Auto-restart on crash

Dynamic month selection

Maker × Fuel matrix extraction

Automatic Excel renaming

Daily cumulative CSV generation

Delta calculation (NEW − OLD)

Append to final_master.xlsx

📦 Installation
1. Install Python

Python 3.10 / 3.11 recommended.

Verify:

python --version

2. Create virtual environment
Windows
python -m venv venv
venv\Scripts\activate

macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

🌐 ChromeDriver Setup

You do NOT need to manually install ChromeDriver.

webdriver-manager automatically:

detects your Chrome version

downloads correct driver

updates it automatically

✔ Works on Windows, macOS, Linux.

📁 Project Structure
project/
│
├── main_scraper.py                 # (Your large Selenium script)
├── preprocessing_services.py        # Consolidates all scraped XLSX into one CSV
├── delta_data.py                    # Computes deltas & updates master
├── district.json                    # RTO → District mapping
│
├── cumulative_folder/               # Daily consolidated CSVs
├── delta_folder/                    # Daily delta outputs
├── final_master.xlsx                # Global master sheet