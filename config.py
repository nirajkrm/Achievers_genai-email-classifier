import os
from dotenv import load_dotenv

load_dotenv()

# === API Configuration ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# === Path Configuration ===
INPUT_DIR = "data/inputs"
OUTPUT_DIR = "data/outputs"
ATTACHMENTS_DIR = os.path.join(INPUT_DIR, "attachments")
LOG_DIR = "Logs"
ENABLE_WEBHOOK = os.getenv("ENABLE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# === Deduplication Configuration ===
DEDUP_DB = os.path.join(OUTPUT_DIR, "dedup_cache.db")
DEDUPLICATION_FIELDS = ["request_type", "date"]
DEDUPLICATION_THRESHOLD = 0.9

# === Currency Configuration ===
CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR", 
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "R$": "BRL"
}
CURRENCY_CODES = {"USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD", "CNY", "BRL"}
ALLOWED_TAGS = {
    "fee", 
    "principal", 
    "repayment", 
    "drawdown", 
    "interest", 
    "amount",
    "commitment"
}

# === Date Configuration ===
DATE_FORMATS = [
    "%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y",
    "%B %d, %Y", "%b %d, %Y", "%Y%m%d",
    "%d %B %Y", "%d %b %Y"
]

# === Classification Configuration ===
REQUEST_TYPE_MAPPINGS = {
    "Loan Modification": "Commitment Change",
    "Loan Repayment": "Money Movement - Outbound",
    "Funding": "Money Movement - Inbound",
    "Capital Contribution": "Money Movement - Inbound",
    "Principal Payment": "Money Movement - Outbound",
    "Repayment Confirmation": "Money Movement - Outbound"
}

SUBJECT_RULES = {
    "commitment": {
        "request_type": "Commitment Change",
        "priority": "Medium",
        "keywords": ["commitment", "facility", "upsize", "downsize"]
    },
    "drawdown": {
        "request_type": "Drawdown",
        "priority": "High", 
        "keywords": ["drawdown", "funding request"]
    },
    "fee": {
        "request_type": "Fee Notification",
        "priority": "Medium",
        "keywords": ["fee", "payment due"]
    },
    "repayment": {
        "request_type": "Money Movement - Outbound",
        "priority": "High",
        "keywords": ["repayment", "principal payment"]
    }
}

# === Team Assignment Configuration ===
TEAM_MAP = {
    # Core Types
    "Loan Repayment": "Disbursement Team",
    "Commitment Change": "Loan Servicing Team",
    "Drawdown": "Allocations Team",
    "Money Movement - Outbound": "Disbursement Team",
    "Money Movement - Inbound": "Cash Ops Team",
    "Allocation Notification": "Allocations Team",
    
    # Aliases
    "Principal Payment": "Disbursement Team",
    "Funds Allocation": "Allocations Team",
    
    # Fallback
    "Others": "General Servicing Team"
}

# === Field Extraction Configuration ===
FIELD_PATTERNS = {
    "deal_name": r"(?:Re|Ref|Reference)[:\s]+([A-Z][^\n]+?)(?:\n|$)",
    "deal_cusip": r"Deal CUSIP\s*[:=]\s*([\w\d]+)",
    "facility_cusip": r"Facility CUSIP\s*[:=]\s*([\w\d]+)",
    "deal_isin": r"Deal ISIN\s*[:=]\s*([\w\d-]+)",
    "facility_isin": r"Facility ISIN\s*[:=]\s*([\w\d-]+)"
}

AMOUNT_REGEX = r"""
    (?:^|\s|\(|\[)
    (?P<curr>USD|EUR|GBP|JPY|\$|€|£|¥|₹|R\$|CAD|AUD|CNY)\s?
    (?P<amt>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b
    |
    \b(?P<amt2>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*
    (?P<curr2>USD|EUR|GBP|JPY|\$|€|£|¥|₹|R\$|CAD|AUD|CNY)\b
"""