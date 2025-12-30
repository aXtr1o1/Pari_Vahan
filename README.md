RTO Automated Scraper & Data Pipeline

This repository automates:

- Scraping daily Vahan RTO Maker × Fuel Excel sheets using Selenium
- Renaming + structuring the downloaded files
- Consolidating into a single daily CSV
- Computing delta sheets between yesterday vs today
- Appending results into a master master CSV/Excel file

The system handles browser crashes, 503 errors, auto-restart, parallel multiprocessing, and logging per state.

### 🚀 Features

- **Parallel scraping for**:
  - Karnataka  
  - Tamil Nadu  
  - Kerala  
  - Puducherry  
- **Auto-restart on crash (503 / browser crash)**
- **Dynamic month selection**
- **Maker × Fuel matrix extraction**
- **Automatic Excel renaming & organizing**
- **Daily cumulative CSV generation (`cumulative_folder/`)**
- **Delta calculation (NEW − OLD) into `delta_folder/`**
- **Append to `final_master.csv` / `final_master.xlsx` for reporting**

### 📦 Installation

1. **Install Python**
   - Python 3.10 / 3.11 recommended.
   - Verify:

   ```bash
   python --version
   ```

2. **Create and activate virtual environment**

   - **Windows**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   - **macOS / Linux**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### 🌐 ChromeDriver Setup

You do **not** need to manually install ChromeDriver.

`webdriver-manager` automatically:

- **Detects** your Chrome version  
- **Downloads** the correct driver  
- **Keeps it updated** automatically  

✔ Works on Windows, macOS, Linux.

### ▶️ How to Run the Full Pipeline

From the project root (after activating the venv and installing requirements):

```bash
python RTO_Scraper.py
```

This single command will:

- **Open headless Chrome sessions**, scrape all configured states (`Karnataka`, `Tamil Nadu`, `Kerala`, `Puducherry`)
- **Store raw daily XLSX files** in your `Downloads\<YYYY-MM-DD>_RTO_Files` folder
- **Consolidate all XLSX files** into a single daily CSV in `cumulative_folder/YYYY-MM-DD.csv` (via `preprocessing_services.py`)
- **Compute the NEW − OLD delta** vs the previous day and write into `delta_folder/YYYY-MM-DD_delta.csv` (via `delta_data.py`)
- **Append the delta to `final_master.csv`** in the project root
- **Trigger email / upload** using the `mail_protocol_service` (if configured)

You can also run each step manually if needed:

- **Only scrape (no processing yet)**:

  ```bash
  python RTO_Scraper.py
  ```

  (Scraped Excel files will end up under `Downloads\<YYYY-MM-DD>_RTO_Files`.)

- **Only consolidate local Excel files into a daily cumulative CSV**:

  Edit `INPUT_FOLDER` in `preprocessing_services.py` (or pass your own folder) and then:

  ```bash
  python preprocessing_services.py
  ```

- **Only compute delta + update master** (assumes `cumulative_folder` already has at least one CSV):

  ```bash
  python delta_data.py
  ```

### 📅 Daily Run Workflow (For End Users)

Once setup is done and the code has been verified to run without errors, the **normal daily usage** is:

1. **Double‑click the Windows batch file**
   - File: `RTO_scrapAutomation.bat`
   - This opens a terminal window and automatically runs the full Python pipeline (scraping → consolidate → delta → master → mail).

2. **Understand that scraping is headless**
   - Chrome runs **in the background (headless)** — you will not see a visible browser window.
   - In Task Manager you will see **multiple `chromedriver.exe` / Chrome processes**.

3. **Do not force‑close the background processes**
   - The script starts **4 parallel ChromeDriver sessions** (one per state).
   - **Do not kill** the terminal window or Chrome/ChromeDriver processes while it is running.
   - If you stop them manually, that day’s data will be **incomplete / corrupted**.

4. **Performance / CPU usage**
   - During the scrape, CPU and memory usage will spike because of the 4 parallel drivers.
   - This is **expected**; the typical run takes **~60–90 minutes**.
   - It is recommended to **avoid heavy work on the same machine** while scraping is running (or at least be prepared for it to feel slower).

5. **Wait for the terminal to finish**
   - The terminal window will keep printing logs until all states are completed and the pipeline finishes.
   - When it is done, the window will either close or clearly show that the script has completed.

### 📊 Power BI Setup (Reporting on `final_master`)

The main reporting source for dashboards is the **master file**:

- **`final_master.csv`** (primary output, always updated by the pipeline)  
- Optionally mirrored as **`final_master.xlsx`** for convenience.

In **Power BI Desktop**:

1. Open Power BI Desktop.
2. Go to **Home → Get Data → Text/CSV** (or **Excel** if you prefer `final_master.xlsx`).
3. Browse to this repository folder and select `final_master.csv` (or `final_master.xlsx`).
4. Click **Load** (or **Transform Data** if you want to clean before loading).
5. Build your visuals using this table.

For daily refresh:

- **Run the pipeline** (`python RTO_Scraper.py`) so that `final_master.csv` is updated.
- In Power BI Desktop, click **Refresh** to pull the latest appended rows.

If you publish to Power BI Service, configure a **data refresh schedule** that runs **after** the automation on the machine that updates `final_master.csv`.

### 🚀 Daily Power BI Refresh & Publish Flow

After the batch file / pipeline has completed for the day:

1. **Open the Power BI report (.pbix) on your machine.**
2. Click **Refresh** on the Home tab to re‑load data from the updated `final_master.csv` (or `final_master.xlsx`).
3. Wait for the refresh to complete and **check all report pages**:
   - Validate key KPIs, totals, filters, and slicers.
   - Make sure the date and volumes look correct for today.
4. Click **Publish** (Home → Publish).
5. In the publish dialog:
   - Choose **Existing workspace**.
   - Select the correct **workspace** used by your team.
   - Confirm to upload / overwrite the existing report + dataset.
6. Wait until Power BI shows **“Published successfully”**.
7. In Power BI Service (browser), open the report and verify:
   - Data has the latest date.
   - All visuals load without error.
8. Once confirmed, copy / share the **public or workspace link** with stakeholders **after** the new version is visible.

### 🧱 Project Structure

project/
│
├── `RTO_Scraper.py`              # Main Selenium scraper + orchestrator (scrape → consolidate → delta)
├── `preprocessing_services.py`   # Consolidates all scraped XLSX into one daily CSV in `cumulative_folder/`
├── `delta_data.py`               # Computes NEW−OLD deltas & appends to `final_master.csv`
├── `district.json`               # RTO → District mapping
│
├── `cumulative_folder/`          # Daily consolidated CSVs (YYYY-MM-DD.csv)
├── `delta_folder/`               # Daily delta outputs (YYYY-MM-DD_delta.csv)
├── `final_master.csv`            # Global master file used by Power BI
├── `final_master.xlsx`           # Optional Excel version of the master
├── `Backup/`                     # Backup copies of master (`final_master.csv`, etc.)
└── `mail_protocol_service/`      # Email / upload integration (uses latest delta/master)

### 🛠 Maintenance & Best Practices

- **Do not keep the master file open while the script runs**
  - Never keep `final_master.csv` or `final_master.xlsx` open in Excel / Power BI while running `python RTO_Scraper.py`.
  - Excel can **lock the file**, causing the pipeline to fail when trying to append data.

- **Where to find logs**
  - All scraper logs are written to your **Downloads** folder:
    - `C:\Users\<username>\Downloads\RTO_Logs\`
  - For each run, you will see files like:
    - `YYYY-MM-DD_RTO_Files_MAIN.log`
    - `YYYY-MM-DD_RTO_Files_Karnataka.log`, etc.
  - Use these logs to **check if any RTO/state failed** or if any data is missing.

- **Checking for missing data**
  - If some RTOs fail, they are listed in the state log (look for “failures” or warnings).
  - Compare number of rows in the latest `cumulative_folder/YYYY-MM-DD.csv` and `delta_folder/YYYY-MM-DD_delta.csv` against previous days.
  - If there is a major drop and no clear external reason, inspect logs and **re-run the pipeline** for that day.

- **Backups**
  - A backup of the master is stored under `Backup/final_master.csv`.
  - Before doing any manual edits, take an additional copy of `final_master.csv` so you can roll back if needed.

- **Do not manually edit generated CSVs unless absolutely necessary**
  - Avoid hand-editing files inside `cumulative_folder/`, `delta_folder/`, or `final_master.csv`.
  - If you must correct data, document what was changed and keep a copy of the original.

- **Environment consistency**
  - Always run the scripts from the **same virtual environment** with the same `requirements.txt`.
  - If you change the schema (add/remove columns), update Power BI and any dependent reports accordingly.