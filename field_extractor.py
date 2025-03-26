import re
import spacy
from datetime import datetime
from config import (
    CURRENCY_SYMBOLS,
    CURRENCY_CODES,
    ALLOWED_TAGS,
    DATE_FORMATS,
    FIELD_PATTERNS,
    AMOUNT_REGEX
)

nlp = spacy.load("en_core_web_sm")

def extract_amounts(text):
    """Extract amounts with currency information using centralized regex"""
    matches = re.finditer(AMOUNT_REGEX, text, flags=re.IGNORECASE | re.VERBOSE)
    results = []
    
    for match in matches:
        curr = (match.group("curr") or match.group("curr2")).upper()
        amt = match.group("amt") or match.group("amt2")
        
        currency = CURRENCY_SYMBOLS.get(curr, curr if curr in CURRENCY_CODES else None)
        if not currency:
            continue
            
        try:
            results.append({
                "amount": float(amt.replace(",", "")),
                "currency": currency,
                "position": match.start()
            })
        except ValueError:
            continue
            
    return results

def extract_dates(text):
    """Extract dates using both spaCy and regex patterns"""
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    
    # Add regex matches
    patterns = [
        r"\d{1,2}[-\s]\w{3}[-\s]\d{4}",  # 15-Mar-2025
        r"\w+\s\d{1,2},\s\d{4}"           # March 15, 2025
    ]
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
    return list(set(dates))

def validate_date(date_str):
    """Validate dates against centralized formats"""
    if not date_str:
        return None
        
    date_str = (date_str.replace("Sept", "Sep")
                       .replace("June", "Jun")
                       .replace("July", "Jul"))
    
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def extract_names(text):
    """Extract organization and person names"""
    doc = nlp(text)
    ignore_terms = {"USD", "ATTN", "DATE", "BANK", "FAX"}
    
    return list(set(
        ent.text.strip() 
        for ent in doc.ents 
        if ent.label_ in ("ORG", "PERSON")
        and not any(term in ent.text.upper() for term in ignore_terms)
    ))

def extract_additional_fields(text):
    """Extract fields using centralized patterns"""
    results = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[field] = match.group(1).strip()
    return results

async def extract_all_fields(text):
    """Main extraction function with error handling"""
    try:
        return {
            "amounts": [
                {"amount": amt["amount"], "currency": amt["currency"]}
                for amt in extract_amounts(text)
            ],
            "dates": [
                validate_date(date) 
                for date in extract_dates(text) 
                if validate_date(date)
            ],
            "names": extract_names(text),
            **extract_additional_fields(text)
        }
    except Exception as e:
        return {
            "amounts": [],
            "dates": [],
            "names": []
        }