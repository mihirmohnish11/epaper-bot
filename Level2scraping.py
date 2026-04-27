import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import re

# ================= CONFIG =================
URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==========================================


def get_mumbai_pdf():
    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        today = datetime.now().strftime("%d %b %Y")
        print("Looking for:", today)

        rows = soup.find_all("p")

        for row in rows:
            text = row.get_text()

            if today in text:
                print("Found today's row")

                links = row.find_all("a")

                for link in links:
                    if "Mumbai" in link.text:
                        page_url = link.get("href")
                        print("Mumbai page:", page_url)

                        return extract_drive_link(page_url)

        print("Mumbai not found")
        return None

    except Exception as e:
        print("Error fetching main page:", e)
        return None


def extract_drive_link(page_url):
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a"):
            href = a.get("href")

            if href and "drive.google.com/file/d/" in href:
                file_id = re.search(r"/d/(.*?)/", href).group(1)
                direct = f"https://drive.google.com/uc?export=download&id={file_id}"

                print("Found PDF:", direct)
                return direct

        print("Drive link not found")
        return None

    except Exception as e:
        print("Error extracting drive link:", e)
        return None


def send_to_telegram(pdf_url):
    try:
        date_str = datetime.now().strftime("%d-%b-%Y")
        filename = f"FreePress_Mumbai_{date_str}.pdf"

        tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

        data = {
            "chat_id": CHAT_ID,
            "caption": f"📰 Free Press Journal Mumbai\n📅 {date_str}"
        }

        files = {
            "document": (filename, requests.get(pdf_url, stream=True).content)
        }

        response = requests.post(tg_url, data=data, files=files)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    except Exception as e:
        print("Telegram error:", e)


def main():
    MAX_RETRIES = 5

    for attempt in range(MAX_RETRIES):
        print(f"Attempt {attempt + 1}")

        pdf = get_mumbai_pdf()

        if pdf:
            send_to_telegram(pdf)
            return

        time.sleep(120)  # wait 2 minutes before retry

    print("❌ Could not fetch Mumbai PDF after retries")


if __name__ == "__main__":
    main()
