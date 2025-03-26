import os
import json
import asyncio
from email_loader import parse_email_file
from llm_classifier import classify_email
from field_extractor import extract_all_fields
from deduplicator import check_duplicate
from config import (
    INPUT_DIR,
    OUTPUT_DIR,
    TEAM_MAP,
    REQUEST_TYPE_MAPPINGS
)
from Logger import logger
from webhook_sender import send_to_webhook

def get_request_type(classification_data):
    """Normalize request types using centralized mapping"""
    request_type = classification_data.get("primary_request", {}).get("request_type", "Others")
    return REQUEST_TYPE_MAPPINGS.get(request_type, request_type)

async def process_email(file_path, email_id):
    try:
        # Parse email
        email_data = parse_email_file(file_path)
        raw_body = email_data.get("body", "")
        subject = email_data.get("subject", "")
        
        # Classify
        classification_data = await classify_email(subject, raw_body)
        request_type = get_request_type(classification_data)
        
        # Extract fields
        extracted_fields = await extract_all_fields(
            raw_body + "\n\n" + 
            "\n\n".join(att.get("content", "") for att in email_data.get("attachments", []))
        )

        # Build output
        output = {
            "email_id": email_id,
            "subject": subject,
            "from": email_data.get("from", "unknown"),
            "to": email_data.get("to", "unknown"),
            "date": email_data.get("date", "unknown"),
            "classification": classification_data,
            "extracted_fields": extracted_fields,
            "assigned_team": TEAM_MAP.get(request_type, "General Servicing Team"),
            "duplication": await check_duplicate(
                email_id=email_id,
                cleaned_text=raw_body,
                request_type=request_type,
                date_str=email_data.get("date", "unknown")
            )
        }

        # Save output
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, f"{email_id}_output.json"), "w") as f:
            json.dump(output, f, indent=2)
            
        if os.getenv("ENABLE_WEBHOOK", "false").lower() == "true":
            send_to_webhook(output, email_id)
            
        return output

    except Exception as e:
        logger.error(f"Error processing {email_id}: {e}")
        return {"email_id": email_id, "error": str(e)}

async def main():
    """Process all emails in input directory"""
    files = [
        f for f in os.listdir(INPUT_DIR) 
        if f.lower().endswith((".eml", ".txt", ".docx", ".pdf"))
    ]
    await asyncio.gather(*[
        process_email(os.path.join(INPUT_DIR, f), os.path.splitext(f)[0])
        for f in files
    ])

if __name__ == "__main__":
    asyncio.run(main())