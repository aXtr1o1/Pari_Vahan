from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json, os, time, shutil, logging
from datetime import datetime, timedelta
from multiprocessing import Process, Manager

URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"

# ******************Config*********************
final_folder = f"{time.strftime('%Y-%m-%d')}_RTO_Files"

FINAL_DIR = os.path.join(os.path.expanduser("~"), "Downloads", final_folder)

LOG_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "RTO_Logs")
os.makedirs(LOG_DIR, exist_ok=True)

STATES = {
    "Karnataka": "/html/body/div[3]/div/ul/li[17]",
    "Kerala": "/html/body/div[3]/div/ul/li[18]",
    "Puducherry": "/html/body/div[3]/div/ul/li[29]",
    "Tamil_Nadu": "/html/body/div[3]/div/ul/li[32]",
}

OPTIONS = {
    "motor_car": '//*[@id="VhClass"]/tbody/tr[7]/td/label',
    "motor_cab": '//*[@id="VhClass"]/tbody/tr[52]/td/label'
}



# -------- Helper Functions --------

def get_logger(name: str, filename: str):
    """Create or get a logger that writes to a specific file."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Also mirror to console for that process
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(f"[{name}] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger


def restart_driver(state_name, download_dir, logger, headless=False):
    logger.warning("🔄 Restarting browser due to crash / 503...")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 25)
    driver.get(URL)
    time.sleep(7)

    return driver, wait


# START_DATE = datetime(2025, 12, 1)  # <-- set your project start date
# EXPIRY_MONTHS = 32


# def manager():
#     expiry_date = START_DATE + timedelta(days=EXPIRY_MONTHS * 30)  # approx 24 months
#     print(f"Project expiry date: {expiry_date}")
#     now = datetime.now()
#     print(f"Current date: {now}")
#     if now < expiry_date:
#         return False  # not expired

#     project_root = os.path.dirname(os.path.abspath(__file__))
#     forbidden_paths = ["C:\\", "C:\\Windows", "C:\\Users", "/", "/home", "/usr", "/etc"]
#     if project_root in forbidden_paths or project_root == os.path.expanduser("~"):
#         raise RuntimeError(f"🚨 Unsafe delete attempted at: {project_root}")

#     try:
#         print(f"⚠️ Project expired. Deleting directory: {project_root}")
#         shutil.rmtree(project_root)
#         return True
#     except Exception as e:
#         print(f"❌ Termination failed: {e}")
#         return False

def download_rename(rto_name, vehicle_type, download_dir, logger):
    """Download and rename the Excel file"""
    logger.info(f"Looking for Excel files in: {download_dir}")
    try:
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)
                 if f.endswith(".xlsx")]
    except FileNotFoundError:
        files = []

    if not files:
        logger.warning("No Excel files found in the download folder.")
        return False

    latest_file = max(files, key=os.path.getctime)

    base_name = f"{rto_name}_{vehicle_type}.xlsx"
    new_path = os.path.join(download_dir, base_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    os.rename(latest_file, new_path)
    logger.info(f"Renamed: {os.path.basename(latest_file)} → {base_name}")

    os.makedirs(FINAL_DIR, exist_ok=True)
    final_path = os.path.join(FINAL_DIR, base_name)

    if os.path.exists(final_path):
        logger.warning(f"{final_path} exists, overwriting")
        os.remove(final_path)

    shutil.move(new_path, final_path)
    logger.info(f"Moved file to: {final_path}")
    return True

from selenium.common.exceptions import NoSuchElementException

def is_crashed(driver):
    try:
        driver.find_element(By.XPATH, "/html/body/form/div[1]/div/nav/div[1]/a[2]/img")
        return False
    except NoSuchElementException:
        return True
    except Exception:
        return True




def process_rto(driver, wait, visible_li, n, options_name, vehicle_type, download_dir, logger):
    """Process a single RTO"""
    try:
        def li_text(li):
            return (li.text or li.get_attribute("textContent") or "").strip()

        # If visible_li shorter than expected, fail fast
        if n >= len(visible_li):
            logger.error(f"Index {n} out of range for visible_li (len={len(visible_li)})")
            return False

        rto_name = li_text(visible_li[n])
        logger.info(f"================= RTO option {n}: {rto_name} =================")

        # Select RTO
        rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
        rto_dropdown.click()
        time.sleep(1)
        # Select by id because the menu uses ids like selectedRto_1, selectedRto_2,...
        rto_option = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="selectedRto_{n}"]')))
        rto_option.click()
        logger.info(f"✅ Selected RTO {n}")
        time.sleep(1)

        # y-axis → Maker
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar"]/div[3]'))).click()
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar_4"]'))).click()
        time.sleep(0.5)

        # x-axis → Fuel
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar"]/div[3]'))).click()
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar_3"]'))).click()
        time.sleep(0.5)

        # Refresh chart
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[3]/div[3]/div/button'))).click()
        time.sleep(1)

        # Month dropdown - ensure the desired month (you used _12 previously)
        m = datetime.now().month
        print(f"Current month: {m}")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth"]/div[3]'))).click()
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="groupingTable:selectMonth_{m}"]'))).click()
        time.sleep(0.5)

        #selecting LMV
        # logger.info(f"selected LMV in options")
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhCatg"]/tbody/tr[12]/td/div/div[2]/span'))).click()
        # time.sleep(0.5)

        # #selecting LPV
        # logger.info(f"selected LPV in options")
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhCatg"]/tbody/tr[13]/td/div/div[2]/span'))).click()
        # time.sleep(0.5)

        # if motorcab selecting Luxury Cab & Maxi Cab

        if vehicle_type=="motor_cab":
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[39]/td/label'))).click()
            time.sleep(0.5)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[51]/td/label'))).click()
            time.sleep(0.5)
            logger.info(f"selecting Luxury Cab & Maxi Cab")

        # Select vehicle class
        logger.info(f"Selecting vehicle class: {vehicle_type}")
        wait.until(EC.element_to_be_clickable((By.XPATH, options_name))).click()
        time.sleep(0.5)

        # Filter apply / refresh
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[3]/div/div[1]/div[1]/span/button'))).click()
        time.sleep(1)

        # Click download
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[3]/div/div[2]/div/div/div[1]/div[1]/a/img'))).click()
        logger.info("📥 Download triggered")
        time.sleep(2)

        # Attempt rename/move
        download_rename(rto_name, vehicle_type, download_dir, logger)
        return True

    except Exception as e:
        logger.error(f"❌ Error at RTO {n}: {e}")
        return False


def process_state(state_name, state_xpath, start_index=1):
    logger = get_logger(
        name=f"STATE-{state_name}",
        filename=f"{final_folder}_{state_name}.log"
    )
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting process for {state_name}")
    logger.info(f"{'='*60}\n")
    download_dir = os.path.join(os.path.expanduser("~"), "Downloads", f"{state_name}_temp")
    os.makedirs(download_dir, exist_ok=True)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("detach", False)
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 25)  # type: ignore

    failed_rtos = []

    try:
        driver.get(URL)
        time.sleep(10)

        # Open filter
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout-toggler"]/span/a'))).click()
        time.sleep(1)

        # Select state
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="masterLayout_formlogin"]/div[2]/div/div/div[1]/div[2]/div[3]'))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, state_xpath))).click()
        logger.info(f"✅ Selected state: {state_name}")
        time.sleep(1)

        # Get RTO list
        rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
        rto_dropdown.click()
        time.sleep(1)

        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto_items"]')))
        time.sleep(1)
        all_li = driver.find_elements(By.XPATH,
                                      '//*[@id="selectedRto_items"]//li[contains(@class,"ui-selectonemenu-item") and not(contains(@class,"ui-state-disabled"))]')
        visible_li = [li for li in all_li if li.is_displayed()]

        rto_dropdown.click()
        time.sleep(2)

        logger.info(f"Total RTO options for {state_name}: {len(visible_li)}")

        # Process each vehicle type
        for vehicle_type, xpath in OPTIONS.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Vehicle Class: {vehicle_type}")
            logger.info(f"{'='*50}")

            crash_restarts = 0
            max_restarts = 10
            n = start_index

            # While loop to allow restart/resume
            while n < len(visible_li):

                # Crash detection before each iteration
                if is_crashed(driver):
                    logger.error("❌ Site crashed / 503 detected!")
                    time.sleep(10)
                    try:
                        driver.quit()
                    except Exception:
                        pass

                    crash_restarts += 1
                    if crash_restarts > max_restarts:
                        logger.critical("🛑 Maximum crash restarts reached. Aborting state.")
                        break

                    # Restart browser and re-initialize everything needed
                    driver, wait = restart_driver(state_name, download_dir, logger)

                    # Re-open filter, reselect state and re-populate visible_li
                    try:
                        # open filter
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout-toggler"]/span/a'))).click()
                        time.sleep(1)

                        # select state area and the state itself
                        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                              '//*[@id="masterLayout_formlogin"]/div[2]/div/div/div[1]/div[2]/div[3]'))).click()
                        time.sleep(1)
                        wait.until(EC.element_to_be_clickable((By.XPATH, state_xpath))).click()
                        time.sleep(2)
                        logger.info("🔁 State reloaded successfully after crash")

                        # RELOAD RTO LIST (important: visible_li must point to elements from this driver)
                        rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
                        rto_dropdown.click()
                        time.sleep(1)

                        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto_items"]')))
                        time.sleep(1)

                        all_li = driver.find_elements(By.XPATH,
                                                      '//*[@id="selectedRto_items"]//li[contains(@class,"ui-selectonemenu-item") and not(contains(@class,"ui-state-disabled"))]')
                        visible_li = [li for li in all_li if li.is_displayed()]

                        rto_dropdown.click()
                        time.sleep(1)

                        logger.info(f"🔁 Re-populated visible_li, count: {len(visible_li)} (resuming at index {n})")

                        # Re-select month so subsequent process_rto calls use same month
                        try:
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth"]/div[3]'))).click()
                            time.sleep(0.5)
                            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth_12"]'))).click()
                            time.sleep(0.5)
                        except Exception:
                            # not fatal - process_rto will attempt again
                            logger.info("Could not pre-set month after restart; process_rto will set it.")

                    except Exception as e:
                        logger.error(f"Failed to re-initialize after restart: {e}")

                        continue

                    # After successful restart/resync, continue without incrementing n (retry same RTO)
                    continue

                # Normal processing
                try:
                    success = process_rto(driver, wait, visible_li, n, xpath, vehicle_type, download_dir, logger)
                    if not success:
                        failed_rtos.append((n, vehicle_type, xpath))
                    # increment only after an attempt (success or failure recorded)
                    n += 1
                    time.sleep(1)

                except Exception as e:
                    # Unexpected exception - attempt a restart and retry same index
                    logger.error(f"⚠️ Unexpected error processing RTO {n}: {e}")
                    try:
                        driver.quit()
                    except Exception:
                        pass

                    crash_restarts += 1
                    if crash_restarts > max_restarts:
                        logger.error("🛑 Too many restarts. Skipping state.")
                        break

                    driver, wait = restart_driver(state_name, download_dir, logger)
                    continue

        retry_count = 0
        max_retries = 3

        while failed_rtos and retry_count < max_retries:
            retry_count += 1
            logger.info(f"\n🔁 Retry attempt {retry_count}/{max_retries} for {state_name}")
            still_failed = []

            if is_crashed(driver):
                time.sleep(10)
                logger.warning("Driver crashed before retry loop. Attempting single restart for retries.")
                try:
                    driver.quit()
                except Exception:
                    pass
                driver, wait = restart_driver(state_name, download_dir, logger)
                # re-populate visible_li
                try:
                    rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
                    rto_dropdown.click()
                    time.sleep(1)
                    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto_items"]')))
                    time.sleep(1)
                    all_li = driver.find_elements(By.XPATH,
                                                  '//*[@id="selectedRto_items"]//li[contains(@class,"ui-selectonemenu-item") and not(contains(@class,"ui-state-disabled"))]')
                    visible_li = [li for li in all_li if li.is_displayed()]
                    rto_dropdown.click()
                    time.sleep(1)
                except Exception:
                    logger.warning("Could not repopulate visible_li for retries; continuing anyway.")

            for n, vehicle_type, xpath in failed_rtos:
                success = process_rto(driver, wait, visible_li, n, xpath, vehicle_type, download_dir, logger)
                if not success:
                    still_failed.append((n, vehicle_type, xpath))
                time.sleep(1)
            logger.info(f"Retry attempt {retry_count} completed for {state_name}")
            failed_rtos = still_failed

        if failed_rtos:
            logger.warning(f"\n⚠️ {state_name} completed with {len(failed_rtos)} failures:")
            for n, vtype, _ in failed_rtos:
                logger.warning(f"  - RTO {n} ({vtype})")
        else:
            logger.info(f"\n✅ {state_name} completed successfully!")

    except Exception as e:
        logger.error(f"❌ Fatal error in {state_name}: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

        try:
            if os.path.exists(download_dir):
                for file in os.listdir(download_dir):
                    if file.endswith(".xlsx"):
                        shutil.move(
                            os.path.join(download_dir, file),
                            os.path.join(FINAL_DIR, file)
                        )
                shutil.rmtree(download_dir)
        except Exception as e:
            logger.info(f"⚠️ Error cleaning up {state_name} temp directory: {e}")


def main():
    logger = get_logger("MAIN", f"{final_folder}_main.log")
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting Parallel RTO Data Collection")
    # if manager():
    #     return
    logger.info(f"Processing {len(STATES)} states simultaneously")
    logger.info(f"{'='*60}\n")
    os.makedirs(FINAL_DIR, exist_ok=True)  # <-- single shared output folder

    start_time = time.time()

    processes = []
    for state_name, state_xpath in STATES.items():
        p = Process(target=process_state, args=(state_name, state_xpath, 1))
        processes.append(p)
        p.start()
        time.sleep(2)

    for p in processes:
        p.join()

    elapsed_time = time.time() - start_time
    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 All states completed!")
    logger.info(f"⏱️  Total time: {elapsed_time/60:.2f} minutes")
    logger.info(f"{'='*60}\n")
    from datetime import date
    from preprocessing_services import consolidate_rto_files
    from delta_data import main as delta_main

    INPUT_FOLDER = FINAL_DIR
    OUTPUT_CSV = f"cumulative_folder/{date.today().strftime('%Y-%m-%d')}.csv"
    consolidate_rto_files(INPUT_FOLDER, OUTPUT_CSV)
    delta_main()


if __name__ == "__main__":
    main()
