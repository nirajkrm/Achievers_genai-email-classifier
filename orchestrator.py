import os
import json
import asyncio
from email_loader import parse_email_file
from llm_classifier import classify_email
from field_extractor import extract_all_fields
from deduplicator import check_duplicate
from config import INPUT_DIR, OUTPUT_DIR, TEAM_MAP
from Logger import logger
from webhook_sender import send_to_webhook

# Clear duplicate cache for fresh run
dedup_cache_path = os.path.join("data", "outputs", "dedup_cache.db")
if os.path.exists(dedup_cache_path):
    os.remove(dedup_cache_path)

def get_request_type(classification_data: dict) -> str:
    """Extract and normalize request type from classification data"""
    # Handle nested primary_request structure
    primary_request = classification_data.get("primary_request", {})
    request_type = primary_request.get("request_type", "Others")
    
    # Normalize the request type
    request_type = request_type.strip().title()
    
    # Special case mappings
    type_mappings = {
        "Loan Modification": "Commitment Change",
        "Loan Repayment": "Money Movement - Outbound",
        "Funding": "Money Movement - Inbound",
        "Capital Contribution": "Money Movement - Inbound",
        "Principal Payment": "Money Movement - Outbound",
        "Repayment Confirmation": "Money Movement - Outbound"
    }
    
    return type_mappings.get(request_type, request_type)

async def process_email(file_path, email_id):
    """Process an email file by parsing, classifying, and extracting fields."""
    try:
        # Step 1: Load and parse the email file
        email_data = parse_email_file(file_path)
        raw_body = email_data.get("body", "")
        subject = email_data.get("subject", "")
        from_address = email_data.get("from", "unknown")
        to_address = email_data.get("to", "unknown")
        date_sent = email_data.get("date", "unknown")

        # Step 2: Classify the email
        classification_data = await classify_email(subject, raw_body)
        
        # Get and normalize request type
        request_type = get_request_type(classification_data)
        assigned_team = TEAM_MAP.get(request_type, "General Servicing Team")
        
        logger.debug(
            f"Classification: {classification_data.get('primary_request', {}).get('request_type')} "
            f"→ Normalized: {request_type} → Team: {assigned_team}"
        )

        # Step 3: Extract structured fields
        attachment_text = "\n\n".join(att.get("content", "") for att in email_data.get("attachments", []))
        combined_text = raw_body + "\n\n" + attachment_text
        extracted_fields = await extract_all_fields(combined_text)

        # Step 4: Deduplication
        dedup_data = await check_duplicate(
            email_id=email_id,
            cleaned_text=raw_body,
            request_type=request_type,
            date_str=date_sent if date_sent else "unknown"
        )

        # Step 5: Final JSON structure
        output = {
            "email_id": email_id,
            "subject": subject,
            "from": from_address,
            "to": to_address,
            "date": date_sent,
            "classification": classification_data,
            "extracted_fields": extracted_fields,
            "assigned_team": assigned_team,
            "duplication": dedup_data
        }

        # Step 6-8: Logging, saving, and webhook
        logger.info(f"Processed Email: {email_id}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{email_id}_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
            
        if os.getenv("ENABLE_WEBHOOK", "false").lower() == "true":
            send_to_webhook(output, email_id)

        return output

    except Exception as e:
        logger.error(f"Error processing {email_id}: {e}")
        return {"email_id": email_id, "error": str(e)}

async def main():
    """Process all input files concurrently."""
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".eml", ".txt", ".docx", ".pdf"))]
    if not files:
        logger.warning("No input files found in input directory.")
        return

    tasks = [process_email(os.path.join(INPUT_DIR, file), os.path.splitext(file)[0]) for file in files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())