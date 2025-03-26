# duplicate_checker/deduplicator.py

import json
import hashlib
import os
from config import DEDUP_DB

async def check_duplicate(email_id, cleaned_text, request_type, date_str):
    """Check if an email is a duplicate (asynchronous)."""
    try:
        # Generate a hash of the email body
        body_hash = hashlib.sha256(cleaned_text.encode('utf-8')).hexdigest()

        # Load existing deduplication cache (if any)
        cache = {}
        if os.path.exists(DEDUP_DB):
            try:
                with open(DEDUP_DB, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Cache file is corrupted or invalid. Resetting cache: {e}")
                cache = {}

        # Check for exact duplicates
        for past_id, data in cache.items():
            if data["body_hash"] == body_hash:
                return {
                    "is_duplicate": True,
                    "duplicate_type": "exact",
                    "matched_with": past_id,
                    "reason": "Exact content match"
                }

        # If not a duplicate, store in cache
        cache[email_id] = {
            "request_type": request_type,
            "date": date_str,
            "body_hash": body_hash
        }

        # Save updated cache
        try:
            with open(DEDUP_DB, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

        return {
            "is_duplicate": False,
            "duplicate_type": None,
            "matched_with": None,
            "reason": "Unique request"
        }

    except Exception as e:
        print(f"Deduplication error for {email_id}: {e}")
        return {
            "is_duplicate": False,
            "duplicate_type": None,
            "matched_with": None,
            "reason": f"Deduplication failed: {str(e)}"
        }