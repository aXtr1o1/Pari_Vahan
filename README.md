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

Core processing scripts:

- `RTO_Scraper.py` → **Parallel Selenium scraper + orchestrator**. Handles:
  - Infinite retries on state / RTO failures
  - Crash detection (503 / browser crash) and automatic Chrome restart
  - Daily folder creation in `Downloads\YYYY-MM-DD_RTO_Files`
  - Post‑processing hook to consolidate, compute delta, and trigger mail/upload
- `delta_data.py` → **Delta engine + mail/Drive trigger**. Handles:
  - Automatically picking **yesterday vs today** CSV from `cumulative_folder/`
  - Column‑wise numeric delta computation (NEW − OLD)
  - Writing per‑day delta into `delta_folder/YYYY-MM-DD_delta.csv`
  - Calling `upload_and_email(...)` from `mail_protocol_service`
- `preprocess.py` → **Master preprocessing for BI**:
  - Cleans and reshapes `final_master.csv` into `master_preprocessed.csv`
  - Adds city, AO, maker short names, fuel grouping, FY, Month, Quarter, Zone
- `mail_protocol_service/mail_protocol.py` → **Google Drive upload + mailer**:
  - Uploads **Delta**, **Cumulative**, and **Master** CSV to a structured Drive folder
  - Makes files/folders public (anyone with the link)
  - Sends HTML email with links + attached `master_preprocessed.csv`

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
  - Uploads files to Google Drive (`Parivahan scraped data` → `Delta` & `Cumulative`)
  - Sends automated email with Drive links + attached preprocessed master

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

### 📅 Run Triggers & Daily Workflow (For End Users)

Once setup is done and the code has been verified to run without errors, there are **three ways (triggers)** to run the scraping pipeline:

1. **Manual trigger (on‑demand)**
   - Double‑click the Windows batch file: `RTO_scrapAutomation_Manual.bat` (in the project root).
   - This opens a terminal window and automatically runs the full Python pipeline (scraping → consolidate → delta → master → mail/Drive).
2. **Scheduled trigger at 6:00 AM (every day)**
   - Windows Task Scheduler automatically calls the same batch file every day at **06:00**.
3. **Startup trigger (on boot / logon)**
   - Windows Task Scheduler calls the same batch file **once when the system boots/logs in** (to catch up if the machine was off at 6 AM).

The scraping process itself typically takes **~60–90 minutes** end‑to‑end.

#### What to expect while the pipeline is running

1. **Double‑click (or scheduled run) of the batch file**
   - File: `RTO_scrapAutomation_Manual.bat`
   - Triggers `python RTO_Scraper.py` inside the correct environment/project folder.

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

### 🕒 Windows Task Scheduler Setup (6 AM & Startup)

The same batch file `RTO_scrapAutomation_Manual.bat` is used for **all three triggers** (manual, daily schedule, startup). You only need to create **two scheduled tasks** in Windows:

- **Task 1 – Daily 6:00 AM run**
  1. Open **Task Scheduler** (Start → search “Task Scheduler”).
  2. Click **Create Basic Task…** (or **Create Task…** for more options).
  3. Name it something like **“RTO_Scraper_Daily_6AM”**.
  4. **Trigger**: choose **Daily**, then set **Start time = 06:00:00**, repeat every 1 day.
  5. **Action**: choose **Start a program**.
     - **Program/script**: full path to `RTO_scrapAutomation_Manual.bat` (e.g. `C:\Users\<you>\OneDrive\Desktop\Pari\RTO_scrapAutomation_Manual.bat`).
     - **Start in (optional)**: project folder path, e.g. `C:\Users\<you>\OneDrive\Desktop\Pari` (without quotes and without the `.bat` filename).
  6. Finish and make sure **“Run whether user is logged on or not”** is enabled (if you use **Create Task…**).

- **Task 2 – Run on Startup / Logon**
  1. In **Task Scheduler**, click **Create Basic Task…**.
  2. Name it something like **“RTO_Scraper_On_Startup”**.
  3. **Trigger**: choose either:
     - **When the computer starts** (if you want it at system boot), or
     - **When I log on** (if you want it right after a specific user logs in).
  4. **Action**: again choose **Start a program** and point to the same `RTO_scrapAutomation_Manual.bat`:
     - **Program/script**: full path to `RTO_scrapAutomation_Manual.bat`.
     - **Start in**: project folder path (same as above).
  5. Save the task.

After this, the pipeline will:

- Run **automatically at 6:00 AM** every day.
- Run **once on startup/logon** (useful if the machine was off at 6:00 AM).
- Still allow **manual runs** any time by double‑clicking `RTO_scrapAutomation_Manual.bat`.

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

- Ensure the pipeline has completed (whether via **manual**, **6 AM**, or **startup** trigger) so that `final_master.csv` is updated.
- In Power BI Desktop, click **Refresh** to pull the latest appended rows.

If you publish to Power BI Service, configure a **data refresh schedule** that runs **after** the automation on the machine that updates `final_master.csv`.

### 🚀 Daily Power BI Refresh & Publish Flow

After the batch file / pipeline has completed for the day (you can see from the terminal/logs that the run is finished):

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

This is the **standard daily user flow** once everything is set up:

1. Let Task Scheduler run the scraper automatically (6:00 AM + at startup) or manually trigger it if needed.
2. Wait 60–90 minutes for the scraping + processing + upload + mail to complete.
3. Open the Power BI `.pbix`, click **Refresh**, then **Publish**, choose the correct workspace, and confirm.
4. The **shared public/workspace link** now points to the **latest data**.

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

Inside `mail_protocol_service/`:

- `mail_protocol.py`           # Google Drive upload, public link creation, automated e‑mail
- `settings.yaml`              # PyDrive2 OAuth config (points to Google client secret JSON)
- `mycreds.txt`                # Cached OAuth token (auto‑generated after first login)
- `client_secret_*.json`       # Google API OAuth client for Drive (downloaded from Google Cloud)

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

### 📧 & 📂 Changing the Mail ID (Drive Upload + SMTP Mail)

There are **two pieces** when you change the mail/Drive identity:

1. **Google Drive account (for uploads & public links)** – controlled via **PyDrive2 OAuth**.
2. **SMTP mail account (from‑address for the notification mail)** – controlled via **SMTP settings** in `mail_protocol.py`.

#### 1️⃣ Change Google Drive account (PyDrive2)

Steps to move to a new Google account (or new client ID):

1. In the new Google account, go to **Google Cloud Console** and create an **OAuth 2.0 Client ID (Desktop App)** for Drive API.
2. Download the **`client_secret_....json`** file.
3. Place this JSON in the `mail_protocol_service` folder (or any path you prefer).
4. Open `mail_protocol_service/settings.yaml` and update:
   - `client_config_file:` to the **full path** of the new `client_secret_....json` file.
5. Delete the old cached credentials file **`mail_protocol_service/mycreds.txt`** (so the next run forces a fresh login).
6. Run either:
   - The full pipeline once (`python RTO_Scraper.py`), or
   - A small test script that calls `upload_and_email(...)`.
7. A browser window will open asking you to **log in and grant Drive access** – log in using the **new Google account** and approve.
8. After success, a new `mycreds.txt` is created, and subsequent runs will upload to the **new Google Drive**.

#### 2️⃣ Change SMTP mail account (From address)

In `mail_protocol_service/mail_protocol.py`:

- Update these lines to your new sender account and app password:

  ```python
  smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
  smtp_port = int(os.getenv("SMTP_PORT", 587))
  smtp_user = "your_new_email@example.com"
  smtp_password = "your_app_password_or_smtp_password"
  ```

Recommended for Gmail:

- Use **App Passwords** (not your main password): in Google Account → Security → App passwords.
- Set `smtp_port` to `465` and use **SSL**, as already configured in the script (`smtplib.SMTP_SSL`).

If you want to hide credentials in environment variables instead:

1. Create a `.env` file inside `mail_protocol_service` (same folder as `mail_protocol.py`) with:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USER=your_new_email@example.com
   SMTP_PASSWORD=your_app_password_or_smtp_password
   ```
2. Adjust `mail_protocol.py` to read:
   ```python
   smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
   smtp_port = int(os.getenv("SMTP_PORT", 465))
   smtp_user = os.getenv("SMTP_USER")
   smtp_password = os.getenv("SMTP_PASSWORD")
   ```
3. Restart any scheduled tasks / terminals to ensure the env is loaded (or run via the batch file which activates the environment).

#### 3️⃣ Change recipient list

The recipients for the automated email are configured in `delta_data.py` in the call to `upload_and_email(...)`:

```python
upload_and_email(
    delta_csv_path=out_file,
    cumulative_csv_path=new_path,
    master_csv_path=PREPROCESS_MASTER_FILE,
    recipient_email="sanjeevan@axtr.in"
)
```

- Edit `recipient_email` to a **comma‑separated list** or the specific addresses you want (e.g. `"a@b.com,c@d.com"`).

Once these three pieces are updated, the system will **upload to the new Drive**, send mail **from the new ID**, and **target the new recipients** automatically for all future runs.