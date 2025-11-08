from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import json, os, time
import os
import shutil
from onedrive_service import upload_to_google_drive
from email_service import send_drive_link_via_email


URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
CHECKPOINT_FILE = "rto_progress.json"

#******************Config*********************

final_folder = f"{time.strftime('%Y-%m-%d')}_RTO_Files"
failed_rtos = []
failed_rtos_indexes = []

# Xpath error on ->
# STATE DROPDOWN.
# TAMIL NADU SELECTION.
# BOTH REFRESH BUTTON
# DOWNLOAD BUTTON



# -------- Helpers for checkpoint --------
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return int(json.load(f).get("last_completed_index", 0))
    return 0

def save_checkpoint(idx):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_completed_index": idx}, f)

def download_rename(rto_name):
    download_dir = (os.path.join(os.path.expanduser("~"), "Downloads"))
    print(f"📂 Looking for Excel files in: {download_dir}")
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)
            if f.endswith(".xlsx")]

    if not files:
        print("⚠️ No Excel files found in the download folder.")
    else:
        latest_file = max(files, key=os.path.getctime)  # most recent file by creation time
        new_path = os.path.join(download_dir, f"{rto_name}.xlsx")

        # --- If file already exists, rename safely ---
        if os.path.exists(new_path):
            os.remove(new_path)

        os.rename(latest_file, new_path)
        print(f"✅ Renamed latest file:\n{os.path.basename(latest_file)} → renamed_file.xlsx")

        rto_folder = os.path.join(download_dir, final_folder)
        os.makedirs(rto_folder, exist_ok=True)  # create folder if not exists

        final_path = os.path.join(rto_folder, f"{rto_name}.xlsx")
        shutil.move(new_path, final_path)

        print(f"📦 Moved file to: {final_path}")




# -------- Selenium setup --------
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 25)

# -------- Start --------
driver.get(URL)
time.sleep(10)

# Select state
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="masterLayout_formlogin"]/div[2]/div/div/div[1]/div[2]/div[3]'))).click()

time.sleep(1)
wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/ul/li[32]'))).click()
print("✅ Selected Tamil Nadu")
time.sleep(1)

# Get RTO list
rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
rto_dropdown.click()
time.sleep(1)

panel = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto_items"]')))
time.sleep(1)
all_li = driver.find_elements(By.XPATH, '//*[@id="selectedRto_items"]//li[contains(@class,"ui-selectonemenu-item") and not(contains(@class,"ui-state-disabled"))]')
visible_li = [li for li in all_li if li.is_displayed()]
time.sleep(1)

# Open filter
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout-toggler"]/span/a'))).click()        
time.sleep(1)


print(f"Total RTO options: {len(visible_li)}")
rto_dropdown.click()
time.sleep(1)

def li_text(li):
    return (li.text or li.get_attribute("textContent") or "").strip()

start_index = load_checkpoint()
start_index = 0
print(f"▶️ Resuming from RTO #{0 + 1}")

for n in range(start_index, len(visible_li)):
    try:
        rto_name = li_text(visible_li[n+1])
        print(f"\n================= RTO option {n+1}: {rto_name} =================")

        # Reopen dropdown and select RTO
        rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
        rto_dropdown.click()
        time.sleep(1)
        rto_option = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="selectedRto_{n+1}"]')))
        rto_option.click()
        print(f"✅ Selected RTO {n+1}")
        time.sleep(1)

        # y-axis dropdown → Maker
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar"]/div[3]'))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar_4"]'))).click()
        time.sleep(1)

        # x-axis dropdown → Fuel
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar"]/div[3]'))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar_3"]'))).click()
        time.sleep(1)

        # Refresh button
        
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[3]/div[3]/div/button'))).click()
        
        time.sleep(1)

        # Month dropdown
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth"]/div[3]'))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth_11"]'))).click()
        time.sleep(1)
        


        # Select vehicle classes
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[7]/td/label'))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[52]/td/label'))).click()
        time.sleep(1)

        # Filter refresh
        
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[3]/div/div[1]/div[1]/span/button'))).click()
        time.sleep(1)

        # Download Excel
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[2]/div/div/div[3]/div/div[2]/div/div/div[1]/div[1]/a/img'))).click()
        
        print("📥 Download triggered")
        time.sleep(1)

        download_rename(rto_name)

        # Close filter
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout"]/div[1]/a/span'))).click()
        
        # print("✅ Closed filter options")
        # time.sleep(1)

        # Save checkpoint
        save_checkpoint(n)
        print(f"💾 Saved progress up to RTO #{n+1}")

    except Exception as e:
        print(f"❌ Error at RTO {n+1}: {e}")
        failed_rtos.append(rto_name)
        failed_rtos_indexes.append(n+1)
        print(f"Failed RTOs so far: {failed_rtos} and this is their indexes: {failed_rtos_indexes}")
        print("⏸️ Waiting 5 seconds before retrying same RTO...")
        time.sleep(5)
        continue  # retry same index next run (checkpoint not updated)

print("🏁 Completed all RTOs successfully.")
sharable_link = upload_to_google_drive(final_folder)
print(f"🔗 Google Drive Link: {sharable_link}")
send_drive_link_via_email(sharable_link)
driver.quit()