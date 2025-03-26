# imap_watcher.py

import os
import time
import asyncio
from imapclient import IMAPClient
import pyzmail
from orchestrator import process_email
from dotenv import load_dotenv

# Optional .env support
load_dotenv()

# Defaults with fallback
EMAIL_HOST = os.getenv("EMAIL_HOST", "outlook.office365.com")
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@outlook.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_password_or_app_password")
DOWNLOAD_DIR = "data/inputs"

def save_eml_message(raw_message, uid):
    eml_path = os.path.join(DOWNLOAD_DIR, f"email_{uid}.eml")
    with open(eml_path, "wb") as f:
        f.write(raw_message)
    return eml_path

async def check_and_process_emails():
    with IMAPClient(EMAIL_HOST, ssl=True) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.select_folder("INBOX", readonly=False)

        messages = server.search(["UNSEEN"])
        if not messages:
            print("No new emails.")
            return

        for uid, message_data in server.fetch(messages, ["RFC822"]).items():
            raw_message = message_data[b"RFC822"]
            eml_path = save_eml_message(raw_message, uid)
            email_id = os.path.splitext(os.path.basename(eml_path))[0]
            await process_email(eml_path, email_id)
            server.add_flags(uid, [b"\\Seen"])
            print(f"Processed and marked as read: UID {uid}")

def start_polling(interval_sec=60):
    print(f"Watching inbox for {EMAIL_USER} via IMAP...")
    while True:
        try:
            asyncio.run(check_and_process_emails())
        except Exception as e:
            print(f"Watcher error: {e}")
        time.sleep(interval_sec)

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    start_polling()
