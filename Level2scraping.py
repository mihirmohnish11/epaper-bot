import requests
from bs4 import BeautifulSoup
import re

URL = "https://dailyepaper.in/the-free-press-journal-epaper-download/"

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

    latest = drive_links[0]  # assume latest

    match = re.search(r"/d/(.*?)/", latest)
    if match:
        file_id = match.group(1)
        direct = f"https://drive.google.com/uc?export=download&id={file_id}"
        return direct

    return None


pdf = get_latest_pdf()

print("📄 Latest PDF:")
print(pdf)