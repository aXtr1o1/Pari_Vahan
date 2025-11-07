# vahan_dropdown.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Step 1: Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Step 2: Open site
url = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
driver.get(url)

# Step 3: Wait until first dropdown is clickable
wait = WebDriverWait(driver, 15)

try:
    # Click first dropdown
    state_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt37"]/div[3]')))
    state_dropdown.click()
    print("✅ Clicked first dropdown")

    time.sleep(1)

    # Click Tamil Nadu (or whichever option at that XPATH)
    tamilnadu_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt37_31"]')))
    tamilnadu_option.click()
    print("✅ Selected Tamil Nadu option")

    time.sleep(1)

    # Click next RTO dropdown
    rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
    rto_dropdown.click()
    print("✅ Clicked RTO dropdown")
    time.sleep(1)

    
    #########################################

    #To get all the rto list

    panel = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto_items"]')))
    time.sleep(0.3)
    all_li = wait.until(EC.presence_of_all_elements_located((
        By.XPATH,
        '//*[@id="selectedRto_items"]//li[contains(@class,"ui-selectonemenu-item") and not(contains(@class,"ui-state-disabled"))]'
    )))
    visible_li = [li for li in all_li if li.is_displayed()]
    def li_text(li):
        t = (li.text or "").strip()
        if not t:
            t = (li.get_attribute("textContent") or "").strip()
        return t

    print(f"Total RTO options (visible): {len(visible_li)}")


    rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
    rto_dropdown.click()
    print("✅ Clicked RTO dropdown")
    time.sleep(1)


    for i, li in enumerate(visible_li, 1):
        print(f"{i:02d}. {li_text(li)}")


##########################################
    for n in range(len(visible_li)-1):

        print(f"RTO option {n+1}: {li_text(visible_li[n+1])}")
        rto_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]/div[3]')))
        rto_dropdown.click()
        print("✅ Clicked RTO dropdown")
        time.sleep(1)

        rto_selection = f'//*[@id="selectedRto_{n+1}"]'
        rto_option = wait.until(EC.element_to_be_clickable((By.XPATH, rto_selection)))
        rto_option.click()
        print(f"✅ selected the {n+1} rto option")
        time.sleep(1)

        y_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar"]/div[3]')))
        y_dropdown.click()
        print("✅  y axis dropdown clicked")
        time.sleep(1)

        y_dropdown_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar_4"]')))
        y_dropdown_option.click()
        print("✅  selected the maker option")
        time.sleep(1)


        x_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar"]/div[3]')))
        x_dropdown.click()
        print("✅  x axis dropdown clicked")
        time.sleep(1)

        x_dropdown_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar_3"]')))
        x_dropdown_option.click()
        print("✅  selected the fuel option")
        time.sleep(1)

        refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt67"]/span[2]')))
        refresh_button.click()
        print("✅  clicked the refresh button")
        time.sleep(1)

        month_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth"]/div[3]')))
        month_dropdown.click()
        print("✅  clicked the month dropdown")
        time.sleep(1)

        month_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:selectMonth_10"]')))
        month_option.click()
        print("✅  selected the month option")
        time.sleep(1)

        open_options = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout-toggler"]/span/a')))
        open_options.click()
        print("✅  opened the filter options")
        time.sleep(1)

        motorcar_selected = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[7]/td/label')))
        motorcar_selected.click()
        print("✅  selected motorcar option")   
        time.sleep(1)

        motorcab_selected = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VhClass"]/tbody/tr[52]/td/label')))
        motorcab_selected.click()   
        print("✅  selected motorcab option") 
        time.sleep(1)

        options_refresh = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt73"]/span[2]')))
        options_refresh.click() 
        print("✅  clicked the options refresh button")
        time.sleep(1)

        download_file = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="groupingTable:j_idt85"]')))
        download_file.click()
        print("✅  clicked the download file button")

        close_options = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="filterLayout"]/div[1]/a/span')))
        close_options.click()
        print("✅  closed the filter options")

        time.sleep(1)

except Exception as e:
    print("❌ Error:", e)

