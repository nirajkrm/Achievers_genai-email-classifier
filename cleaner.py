import re
from datetime import datetime

CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR"
}

def normalize_whitespace(text):
    """Collapse multiple spaces/tabs into a single space."""
    return re.sub(r'\s+', ' ', text).strip()


def remove_non_ascii(text):
    """Remove non-ASCII characters."""
    return re.sub(r'[^\x00-\x7F]+', ' ', text)


def preserve_lines(text):
    """Preserve paragraph/line structure while cleaning within lines."""
    lines = text.split('\n')
    cleaned_lines = [normalize_whitespace(line) for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)


def standardize_currency(text):
    """Replace common currency symbols with codes."""
    for symbol, code in CURRENCY_SYMBOL_MAP.items():
        text = text.replace(symbol, f"{code} ")
    return text


def standardize_dates(text):
    """Convert dates like '14-Mar-2024' into '2024-03-14'."""
    months = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
        'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }

    def replace_date(match):
        day, mon, year = match.group(1), match.group(2).upper(), match.group(3)
        month = months.get(mon[:3], '01')
        return f"{year}-{month}-{day.zfill(2)}"

    return re.sub(r'(\d{1,2})[-\s](\w{3})[-\s](\d{4})', replace_date, text, flags=re.IGNORECASE)


def remove_email_signature(text):
    """Remove trailing email signatures or common boilerplate."""
    signature_keywords = [
        "Thanks & Regards", "Kind regards", "Sincerely", "Best regards",
        "This email message", "If you have any questions"
    ]
    for keyword in signature_keywords:
        index = text.lower().find(keyword.lower())
        if index != -1:
            return text[:index]
    return text


def extract_reference_sentence(text):
    """Extract the most relevant sentence for classification."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    for s in sentences:
        if len(s.split()) > 4:
            return s.strip()
    return sentences[0].strip() if sentences else ""


def clean_text(raw_text):
    """Run all preprocessing steps."""
    text = preserve_lines(raw_text)
    text = standardize_currency(text)
    text = standardize_dates(text)
    text = remove_email_signature(text)
    text = remove_non_ascii(text)
    return text.strip()
