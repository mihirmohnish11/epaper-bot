import requests
from bs4 import BeautifulSoup
import re
import os
import time
from datetime import datetime

# 🔗 Base URL
BASE_URL = "https://dailyepaper.in"
URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"

# 🔐 Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def extract_drive_link(page_url):
    print("🔎 Opening Mumbai page:", page_url)

    res = requests.get(page_url)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.find_all("a")

    for link in links:
        href = link.get("href")
        if href and "drive.google.com/file/d/" in href:
            match = re.search(r"/d/(.*?)/", href)
            if match:
                file_id = match.group(1)
                direct = f"https://drive.google.com/uc?export=download&id={file_id}"
                print("✅ Found Drive PDF")
                return direct

    print("❌ No Drive link found on Mumbai page")
    return None


def get_latest_pdf():
    res = requests.get(URL)

    if res.status_code != 200:
        print("❌ Failed to fetch main page")
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    today = datetime.now().strftime("%d %b %Y")  # e.g. 27 Apr 2026
    print("📅 Looking for:", today)

    rows = soup.find_all("p")

    for row in rows:
        text = row.get_text()

        if today in text:
            print("✅ Found today's row")

            links = row.find_all("a")

            for link in links:
                if "Mumbai" in link.get_text():
                    mumbai_url = link.get("href")

                    # Fix relative URL
                    if not mumbai_url.startswith("http"):
                        mumbai_url = BASE_URL + mumbai_url

                    print("👉 Mumbai link:", mumbai_url)

                    return extract_drive_link(mumbai_url)

    print("❌ Mumbai link not found for today")
    return None


def download_pdf(pdf_url):
    print("⬇️ Downloading PDF...")

    res = requests.get(pdf_url)

    if res.status_code != 200:
        print("❌ Download failed")
        return None

    return res.content


def send_to_telegram(file_bytes):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
        return

    today = datetime.now().strftime("%d-%b-%Y")
    filename = f"Mumbai_Newspaper_{today}.pdf"

    files = {
        "document": (filename, file_bytes)
    }

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data={
            "chat_id": CHAT_ID,
            "caption": f"📰 Mumbai Newspaper - {today}"
        },
        files=files
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)


def main():
    pdf_url = None

    # 🔁 Retry logic (important)
    for i in range(3):
        print(f"🔁 Attempt {i+1}")
        pdf_url = get_latest_pdf()

        if pdf_url:
            break

        time.sleep(60)

    if not pdf_url:
        print("❌ Could not find Mumbai PDF after retries")
        return

    print("📄 Final PDF:", pdf_url)

    file_bytes = download_pdf(pdf_url)

    if not file_bytes:
        print("❌ Download failed")
        return

    send_to_telegram(file_bytes)


if __name__ == "__main__":
    main()
