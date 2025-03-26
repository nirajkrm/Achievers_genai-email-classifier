# field_extractor.py

import re
import json
import openai
import spacy
from datetime import datetime
from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    CURRENCY_CODES,
    CURRENCY_SYMBOLS,
    ALLOWED_TAGS
)

client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
nlp = spacy.load("en_core_web_sm")


def extract_amounts_with_positions(text):
    pattern = r"""
        \b
        (?P<curr>USD|EUR|GBP|JPY|CAD|AUD|INR|\$|€|£|¥|₹)
        \s?
        (?P<amt>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)
        \b
    """
    matches = re.finditer(pattern, text, flags=re.IGNORECASE | re.VERBOSE)
    results = []
    for match in matches:
        raw = match.groupdict()
        curr = raw["curr"].strip().upper()
        currency = CURRENCY_SYMBOLS.get(curr, curr if curr in CURRENCY_CODES else "UNKNOWN")
        try:
            amount = float(raw["amt"].replace(",", ""))
            context_window = text[max(0, match.start() - 50): match.end() + 50].lower()
            if amount >= 1000 or any(k in context_window for k in ["fee", "adjustment", "share", "commitment"]):
                position = match.start()
                results.append((amount, position, currency))
        except ValueError:
            continue
    return results


def extract_dates(text):
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    regex_dates_1 = re.findall(r"\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{4}", text, flags=re.IGNORECASE)
    regex_dates_2 = re.findall(r"(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s\d{1,2},\s\d{4}", text, flags=re.IGNORECASE)
    regex_dates = list(set(regex_dates_1 + regex_dates_2))
    return list(set(dates + regex_dates))


def extract_names(text):
    doc = nlp(text)
    names = [ent.text.strip().replace("\n", " ") for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]]
    ignore_keywords = {"USD", "ATTN", "DATE", "UNKNOWN", "BANK", "Fax", "Email", "Phone", "Telephone"}
    filtered = []
    for name in names:
        if not name or len(name.strip()) < 3:
            continue
        clean = name.strip()
        for keyword in ignore_keywords:
            if clean.upper().endswith(keyword.upper()):
                clean = re.sub(rf"\b{keyword}\b[:\s]*$", "", clean, flags=re.IGNORECASE).strip()
        words = clean.split()
        if any(word.upper() in ignore_keywords for word in words):
            continue
        if clean.isupper() and len(clean) <= 10:
            continue
        filtered.append(clean)
    return list(set(filtered))


def validate_date(date_str):
    formats = [
        "%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y",
        "%B %d, %Y", "%b %d, %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def validate_amount(amount_str):
    try:
        return float(amount_str.replace(",", ""))
    except Exception:
        return None


async def tag_amount_context(amounts_with_positions, text):
    tagged = []
    for amount, pos, currency in amounts_with_positions:
        context_window = text[max(0, pos - 150): pos + 150]
        if "repayment" in context_window.lower():
            tag = "repayment_amount"
        elif "fee" in context_window.lower():
            tag = "fee_amount"
        elif "commitment" in context_window.lower():
            tag = "commitment_amount"
        else:
            prompt = f"""
Context: {context_window}
Amount: {amount}

What is the role of this amount in context?
Respond with one of the following tags: {", ".join(ALLOWED_TAGS)}.
Only return the tag string. Nothing else.
"""
            try:
                response = await client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a financial data field tagger."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                tag = response.choices[0].message.content.strip()
                if tag not in ALLOWED_TAGS:
                    tag = "unknown"
            except Exception as e:
                print(f"Error tagging amount: {e}")
                tag = "unknown"
        tagged.append({
            "amount": amount,
            "currency": currency,
            "tag": tag
        })
    return tagged


def extract_additional_fields(text):
    additional = {}

    deal_name_match = re.search(r"(Re|Ref)[:\s]+([A-Z].+?)(?:\n|$)", text, re.IGNORECASE)
    if deal_name_match:
        additional["deal_name"] = deal_name_match.group(2).strip()

    patterns = {
        "deal_cusip": r"Deal CUSIP\s*:\s*([\w\d]+)",
        "facility_cusip": r"Facility CUSIP\s*:\s*([\w\d]+)",
        "deal_isin": r"Deal ISIN\s*:\s*([\w\d]+)",
        "facility_isin": r"Facility ISIN\s*:\s*([\w\d]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            additional[key] = match.group(1).strip()

    return additional


async def extract_all_fields(text):
    try:
        amounts = extract_amounts_with_positions(text)
        dates = extract_dates(text)
        names = extract_names(text)
        validated_dates = [validate_date(date) for date in dates if validate_date(date)]
        tagged_amounts = await tag_amount_context(amounts, text)
        extra_fields = extract_additional_fields(text)

        return {
            "amounts": tagged_amounts,
            "dates": validated_dates,
            "names": names,
            **extra_fields
        }

    except Exception as e:
        print(f"Error extracting fields: {e}")
        return {
            "amounts": [],
            "dates": [],
            "names": []
        }
