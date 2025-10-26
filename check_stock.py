import time
import re
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Read Secrets from GitHub Environment ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# The URL you want to scrape
URL = "https://www.sheinindia.in/c/sverse-5939-37961?query=%3Arelevance%3Agenderfilter%3AMen&gridColumns=5&customerType=Existing&segmentIds=15%2C8%2C19&userClusterId=supervalue%7Cm1active%2Cactive%2Cfirstpurchaser%2Cmen%2Clowasp%2Cp_null&customertype=Existing"

# XPath to find the "Men (count)" label
MEN_FILTER_XPATH = "//label[contains(text(), 'Men (')]"


def send_telegram_alert(count):
    """Sends a formatted message to the Telegram channel with full error logging."""
    
    if not BOT_TOKEN or not CHAT_ID:
        print("[TELEGRAM] ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID secrets not set.")
        return

    # Format the number with commas (e.g., 1,252)
    count_formatted = f"{count:,}"
    
    # Create the message text using MarkdownV2 formatting
    # Note: Telegram MarkdownV2 requires escaping characters like . ( ) - !
    message_text = (
        f"🚨 *SHEIN STOCK ALERT* 🚨\n\n"
        f"Men's stock is over 100\\!\n\n"
        f"Current Count: **{count_formatted}**\n\n"
        f"[Click here to check the page]({URL})"
    )
    
    # Define the Telegram API URL and payload
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "MarkdownV2"
    }
    
    try:
        response = requests.post(api_url, json=payload)
        
        # --- NEW DEBUGGING LOGIC ---
        if response.ok:
            print(f"[TELEGRAM] Successfully sent alert (Status {response.status_code}).")
        else:
            # This will print the exact error from Telegram
            print(f"[TELEGRAM] FAILED to send alert (Status {response.status_code}).")
            print(f"API Response: {response.json()}")
        # ---------------------------

        response.raise_for_status() # Raise an exception for bad status codes
        
    except Exception as e:
        print(f"[TELEGRAM] An exception occurred during request: {e}")


def check_stock():
    """
    Launches a headless browser, finds the stock count,
    and sends a Telegram alert if it's 100+.
    """
    
    # --- THIS IS THE CRITICAL FIX ---
    # Set up the options for the GitHub Actions Linux runner
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    # ---------------------------------
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(URL)
        
        wait = WebDriverWait(driver, 20)
        men_label_element = wait.until(
            EC.presence_of_element_located((By.XPATH, MEN_FILTER_XPATH))
        )
        
        label_text = men_label_element.text
        match = re.search(r'\(([\d,]+)\)', label_text)
        
        if match:
            stock_string = match.group(1).replace(',', '')
            stock_count = int(stock_string)
            
            print(f"[{time.ctime()}] SUCCESS: Found Men's stock count: {stock_count}")
            
            # --- MODIFICATION FOR TESTING ---
            # This will force the alert to send every time.
            
            print("\n" + "!"*20)
            print(f"TESTING: Forcing Telegram alert with count: {stock_count}")
            print("!"*20 + "\n")
            
            # --- Send the alert! ---
            send_telegram_alert(stock_count) 
            
            # --- END OF MODIFICATION ---
            
            # --- !!! REMEMBER TO CHANGE IT BACK TO THIS !!! ---
            # if stock_count >= 100:
            #     print("\n" + "!"*20)
            #     print(f"ALERT! STOCK IS 100+ ! Current count: {stock_count}")
            #     print("!"*20 + "\n")
            #     send_telegram_alert(stock_count) 
            # else:
            #     print(f"[{time.ctime()}] Stock ({stock_count}) is below 100. No alert.")
            # ----------------------------------------------------

        else:
            print(f"[{time.ctime()}] ERROR: Could not parse stock count from text: '{label_text}'")

    except Exception as e:
        print(f"[{time.ctime()}] An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()

# --- Main part ---
if __name__ == "__main__":
    # Check for secrets *before* running
    if not BOT_TOKEN or not CHAT_ID:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID secrets.")
        print("Please add them to your GitHub repository settings.")
    else:
        check_stock()