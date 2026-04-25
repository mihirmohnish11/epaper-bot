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
