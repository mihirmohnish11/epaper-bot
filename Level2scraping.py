import requests
from bs4 import BeautifulSoup
import re
import os
import time
from datetime import datetime

URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def get_latest_pdf():
    res = requests.get(URL)

    if res.status_code != 200:
        print("❌ Failed to fetch page")
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.find_all("a")
    drive_links = []

    for link in links:
        href = link.get("href")
        if href and "drive.google.com/file/d/" in href:
            drive_links.append(href)

    if not drive_links:
        print("❌ No Drive links found")
        return None

    latest = drive_links[0]

    match = re.search(r"/d/(.*?)/", latest)
    if match:
        file_id = match.group(1)
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        return direct_link

    return None


def download_pdf(pdf_url):
    print("⬇️ Downloading file...")
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
    filename = f"Newspaper_{today}.pdf"

    files = {
        "document": (filename, file_bytes)
    }

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data={
            "chat_id": CHAT_ID,
            "caption": f"📰 Newspaper - {today}"
        },
        files=files
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)


def main():
    pdf_url = None

    # 🔁 Retry logic (3 attempts)
    for i in range(3):
        print(f"Attempt {i+1}...")
        pdf_url = get_latest_pdf()
        if pdf_url:
            break
        time.sleep(60)

    if not pdf_url:
        print("❌ Could not find PDF after retries")
        return

    print("📄 Found PDF:", pdf_url)

    file_bytes = download_pdf(pdf_url)

    if not file_bytes:
        print("❌ Failed to download PDF")
        return

    send_to_telegram(file_bytes)


if __name__ == "__main__":
    main()
