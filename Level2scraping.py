import requests
from bs4 import BeautifulSoup
import re
import os

# 🔗 Source URL
URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"

# 🔐 Read secrets from environment (GitHub Actions)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print("TOKEN:", TELEGRAM_TOKEN)
print("CHAT_ID:", CHAT_ID)


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

    # Assume first = latest
    latest = drive_links[0]

    match = re.search(r"/d/(.*?)/", latest)
    if match:
        file_id = match.group(1)
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        return direct_link

    return None


def send_to_telegram(pdf_url):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
        return

    print("⬇️ Downloading file...")

    file_response = requests.get(pdf_url)

    if file_response.status_code != 200:
        print("❌ Failed to download PDF")
        return

    files = {
        "document": ("newspaper.pdf", file_response.content)
    }

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data={
            "chat_id": CHAT_ID,
            "caption": "📰 Today's Newspaper"
        },
        files=files
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)


def main():
    pdf = get_latest_pdf()

    if not pdf:
        print("❌ No PDF found")
        return

    print("📄 Latest PDF:", pdf)

    send_to_telegram(pdf)


if __name__ == "__main__":
    main()
