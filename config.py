import os
from dotenv import load_dotenv

load_dotenv()

# === API Keys & Model ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# === Input/Output Paths ===
INPUT_DIR = "data/inputs"
OUTPUT_DIR = "data/outputs"
ATTACHMENTS_DIR = os.path.join(INPUT_DIR, "attachments")
LOG_DIR = "Logs"
ENABLE_WEBHOOK = os.getenv("ENABLE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# === Deduplication Settings ===
DEDUP_DB = os.path.join(OUTPUT_DIR, "dedup_cache.db")
DEDUPLICATION_FIELDS = ["request_type", "date"]
DEDUPLICATION_THRESHOLD = 0.9

# === Currency Symbols and Tags ===
CURRENCY_SYMBOLS = {"$", "€", "£", "¥"}
CURRENCY_CODES = {"USD", "EUR", "GBP", "JPY"}
ALLOWED_TAGS = {"fee", "principal", "repayment", "drawdown", "interest", "amount"}

# === Subject Rule-based Classifier ===
SUBJECT_RULES = {
    "commitment": {"request_type": "Commitment Change", "priority": "Medium"},
    "drawdown": {"request_type": "Drawdown", "priority": "High"},
    "fee": {"request_type": "Fee Notification", "priority": "Medium"},
    "allocation": {"request_type": "Allocation Confirmation", "priority": "Medium"},
    "repayment": {"request_type": "Money Movement - Outbound", "priority": "High"},
    "receipt": {"request_type": "Money Movement - Inbound", "priority": "High"},
}

# === Comprehensive Team Assignment Map ===
TEAM_MAP = {
    # Core request types
    "Loan Repayment": "Disbursement Team",
    "Loan Modification": "Loan Servicing Team",
    "Funding": "Cash Ops Team",
    "Funds Transfer": "Cash Ops Team",
    "Allocation Notification": "Allocations Team",
    "Fee Payment": "Finance Team",
    
    # Subject-based types
    "Commitment Change": "Loan Servicing Team",
    "Drawdown": "Allocations Team",
    "Fee Notification": "Finance Team",
    "Money Movement - Inbound": "Cash Ops Team",
    "Money Movement - Outbound": "Disbursement Team",
    "Allocation Confirmation": "Allocations Team",
    
    # Variants and aliases
    "Funds Allocation": "Allocations Team",
    "Final Allocation": "Allocations Team",
    "Principal Payment": "Disbursement Team",
    "Repayment Confirmation": "Disbursement Team",
    "Capital Contribution": "Cash Ops Team",
    
    # Fallback
    "Others": "General Servicing Team"
}