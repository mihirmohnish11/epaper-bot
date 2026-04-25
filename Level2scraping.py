import requests
from bs4 import BeautifulSoup
import re
import os

URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"

TELEGRAM_TOKEN = os.environ.get(bot8620479743:AAFvRaxZukt_PAtxjs7ceCLZ3hEmpuFWIMI)
CHAT_ID = os.environ.get(398210107)


def get_latest_pdf():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.find_all("a")

    drive_links = []

    for link in links:
        href = link.get("href")
        if href and "drive.google.com/file/d/" in href:
            drive_links.append(href)

    if not drive_links:
        print("❌ No links found")
        return None

    latest = drive_links[0]

    match = re.search(r"/d/(.*?)/", latest)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    return None


def send_to_telegram(pdf_url):
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data={
            "chat_id": CHAT_ID,
            "document": pdf_url,
            "caption": "📰 Today's Newspaper"
        }
    )

    print("Telegram response:", response.text)


def main():
    pdf = get_latest_pdf()

    if not pdf:
        print("No PDF found")
        return

    print("📄 Latest PDF:", pdf)

    send_to_telegram(pdf)


if __name__ == "__main__":
    main()
