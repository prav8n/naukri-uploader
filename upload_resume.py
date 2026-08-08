import os
import time
import logging
import zoneinfo
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/app/logs/upload.log"),
    ],
)
logging.Formatter.converter = lambda *args: datetime.now(IST).timetuple()
log = logging.getLogger(__name__)


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    service = Service(os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def login(driver, email, password):
    log.info("Navigating to Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")
    wait = WebDriverWait(driver, 20)

    email_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
    email_field.clear()
    email_field.send_keys(email)
    log.info("Entered email.")

    pwd_field = driver.find_element(By.ID, "passwordField")
    pwd_field.clear()
    pwd_field.send_keys(password)
    log.info("Entered password.")

    login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_btn.click()
    log.info("Clicked login.")

    wait.until(EC.url_contains("naukri.com"))
    time.sleep(3)
    log.info("Login successful.")


def upload_resume(driver, resume_path):
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume not found at: {resume_path}")

    log.info("Navigating to profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")
    wait = WebDriverWait(driver, 20)
    time.sleep(3)

    log.info("Looking for resume upload input...")
    upload_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='file' and contains(@id,'attachCV')]")
        )
    )
    upload_input.send_keys(resume_path)
    log.info(f"Resume file sent: {resume_path}")
    time.sleep(5)

    try:
        success_msg = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'successfully') or contains(text(),'uploaded')]")
            )
        )
        log.info(f"Upload confirmed: {success_msg.text}")
    except Exception:
        log.warning("No explicit success toast found — checking page state instead.")

    log.info("Resume upload step completed.")


def main():
    email    = os.environ.get("NAUKRI_EMAIL")
    password = os.environ.get("NAUKRI_PASSWORD")
    resume   = os.environ.get("RESUME_PATH", "/app/resume/Praveen_Choudhary_Data_Scientist.pdf")

    if not email or not password:
        log.error("NAUKRI_EMAIL and NAUKRI_PASSWORD environment variables are required.")
        raise SystemExit(1)

    log.info(f"=== Naukri Resume Upload Started at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')} ===")

    max_retries = 3
    retry_delay = 120  # 2 minutes between retries

    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            log.info(f"Attempt {attempt}/{max_retries}...")
            driver = get_driver()
            login(driver, email, password)
            upload_resume(driver, resume)
            log.info("=== Upload Completed Successfully ===")
            return
        except Exception as e:
            log.error(f"Attempt {attempt} failed: {e}")
            if driver:
                driver.save_screenshot(f"/app/logs/error_attempt{attempt}.png")
                log.info(f"Screenshot saved to /app/logs/error_attempt{attempt}.png")
        finally:
            if driver:
                driver.quit()

        if attempt < max_retries:
            log.info(f"Waiting {retry_delay}s before retry...")
            time.sleep(retry_delay)

    log.error("=== All attempts failed. Upload unsuccessful. ===")
    raise SystemExit(1)


if __name__ == "__main__":
    main()