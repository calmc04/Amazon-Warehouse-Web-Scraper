from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from tabulate import tabulate
import smtplib
from email.message import EmailMessage
import os
import sys

init(autoreset=True)

previous_jobs = set()

EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""
TO_EMAIL = ""
SEEN_JOBS_FILE = "seen_jobs.txt"

def load_seen_jobs():
    if not os.path.exists(SEEN_JOBS_FILE):
        return set()
    with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_seen_job(job_info):
    with open(SEEN_JOBS_FILE, "a", encoding="utf-8") as f:
        f.write(job_info + "\n")

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"{Fore.YELLOW}[INFO] Email notification sent!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to send email: {e}{Style.RESET_ALL}")

def display_jobs(job_list):
    seen_jobs = load_seen_jobs()
    headers = ["Title", "Location", "Pay Rate", "Duration"]
    rows = []

    for job_info, _ in job_list:
        parts = job_info.split(" | ")

        if job_info not in seen_jobs:
            colored_parts = [f"{Fore.GREEN}{part}{Style.RESET_ALL}" for part in parts]
            rows.append(colored_parts)

            subject = f"New Job Posted: {parts[0]}"
            body = f"Job Title: {parts[0]}\nLocation: {parts[1]}\nPay Rate: {parts[2]}\nDuration: {parts[3]}"
            send_email(subject, body)

            save_seen_job(job_info)
        else:
            rows.append(parts)

    print("\n" + tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    print(f"\n[INFO] Total jobs fetched: {len(job_list)}")

def fetch_jobs_loop(url):
    options = Options()

    driver = webdriver.Chrome(options=options)

    try:
        print(f"[INFO] Opening page: {url}")
        driver.get("https://www.jobsatamazon.co.uk/app")
        driver.execute_script("window.location.hash = '#/jobSearch';")
        try:
            print("[INFO] Attempting to click 'Accept all' cookie button...")
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Accept all']"))
            )
            accept_button.click()
            print("[INFO] 'Accept all' clicked.")
            time.sleep(2)
        except Exception as e:
            print(f"[WARNING] 'Accept all' button not found or already accepted: {e}")

        while True:
            print("[INFO] Refreshing page...")
            driver.refresh()
            try:
                print("[INFO] Trying to click the close (X) SVG button...")

                close_svg = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "svg.hvh-careers-emotion-6bklpk[data-test-component='StencilIconCrossSmall']"
                    ))
                )
                close_svg.click()

                print("[INFO] Close (X) SVG button clicked.")
                time.sleep(2)
            except Exception as e:
                print(f"[WARNING] Could not find or click close SVG button: {e}")

            print("[INFO] Waiting for job cards to appear...")
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='JobCard']"))
                )
            except Exception as e:
                print(f"[WARNING] Timeout or error waiting for job cards: {e}")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.find_all("div", {"data-test-id": "JobCard"})
            print(f"[INFO] Found {len(job_cards)} job cards")

            job_list = []
            for card in job_cards:
                title_div = card.select_one("div.jobDetailText strong")
                payrate_div = card.find("div", {"data-test-id": "jobCardPayRateText"})
                duration_div = card.find("div", {"data-test-id": "jobCardDurationText"})
                location_div = card.find("div", class_="hvh-careers-emotion-1lcyul5")

                title = title_div.text.strip() if title_div else "No title"
                location_strong = location_div.find("strong") if location_div else None
                location = location_strong.text.strip() if location_strong else "No location"
                payrate = payrate_div.text.strip() if payrate_div else "No pay rate"
                duration = duration_div.text.strip() if duration_div else "No duration"

                job_info = f"{title} | {location} | {payrate} | {duration}"
                job_link = url

                job_list.append((job_info, job_link))

            display_jobs(job_list)

            print("[INFO] Restarting script from fresh in 30 seconds...")
            time.sleep(30)

            print("[INFO] Relaunching script from scratch...")
            driver.quit()
            
            os.execv(sys.executable, [sys.executable] + sys.argv)

    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_jobs_loop("https://www.jobsatamazon.co.uk/app#/jobSearch")