# webhook_sender.py

import requests
from config import WEBHOOK_URL
from Logger import logger

def send_to_webhook(payload: dict, email_id: str):
    if not WEBHOOK_URL:
        logger.warning("No WEBHOOK_URL defined. Skipping webhook call.")
        return

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 201, 202]:
            logger.info(f"Webhook POST successful for {email_id} (status {response.status_code})")
        else:
            logger.error(f"Webhook failed for {email_id}. Status: {response.status_code} | Response: {response.text}")
    except Exception as e:
        logger.error(f"Webhook error for {email_id}: {str(e)}")
