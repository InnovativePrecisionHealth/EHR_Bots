from selenium import webdriver
from  selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

chromeOptions = Options()


chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument('--allow-running-insecure-content')
chromeOptions.headless = True
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)
browser.set_window_size(1366, 768, browser.window_handles[0])

browser.get("https://athenanet.athenahealth.com/1/77/login.esp")
username=browser.find_element(By.ID, "USERNAME")
username.send_keys("jsethi1")
password=browser.find_element(By.ID, "PASSWORD")
password.send_keys("FNSjs2022!!!")
login=browser.find_element(By.ID,"loginbutton")
login.click()
login=browser.find_element(By.ID,"loginbutton")
login.click()
browser.save_screenshot(f"Errored_Screenshot.png")
print("SELENIUM Sign in is complete")

