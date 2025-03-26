# config.py

import os
from dotenv import load_dotenv

# === Load environment variables from .env file ===
load_dotenv()

# === OpenAI Settings ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"  # Ensure this matches your OpenAI model

# === File Paths ===
INPUT_DIR = "data/inputs"  # Directory for input files
OUTPUT_DIR = "data/outputs"  # Directory for output files
DEDUP_DB = os.path.join(OUTPUT_DIR, "dedup_cache.db")  # Deduplication database path

# === Embedding Model ===
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Model for generating embeddings

# === Deduplication Thresholds ===
SIMILARITY_THRESHOLD = 0.9  # Threshold for identifying duplicate emails
DATE_WINDOW_DAYS = 2  # Time window for considering duplicates

# === Webhook URL for ticketing tool integration ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Currency Configurations ===
CURRENCY_SYMBOLS = {
    "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR"
}
CURRENCY_CODES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR"]

# === Allowed Tags for Field Classification ===
ALLOWED_TAGS = [
    "repayment_amount",
    "your_share",
    "previous_global_balance",
    "new_global_balance",
    "fee_amount",
    "commitment_amount",
    "allocation_amount",
    "unknown"
]

# === Subject-Based Classification Rules ===
SUBJECT_RULES = {
    "Commitment Change": {
        "keywords": ["commitment", "upsize", "increase"],
        "request_type": "Commitment Change",
        "sub_request_type": "Commitment Increase"
    },
    "Final Allocation": {
        "keywords": ["final allocation", "closing deal"],
        "request_type": "Drawdown",
        "sub_request_type": "Final Allocation"
    },
    "Fee Notification": {
        "keywords": ["fee", "amendment"],
        "request_type": "Fee Notification",
        "sub_request_type": "Amendment Fee"
    },
    "Principal and Interest": {
        "keywords": ["principal", "interest", "payment"],
        "request_type": "Money Movement - Inbound",
        "sub_request_type": "Principal + Interest"
    },
    # Add more subject-based rules as needed...

    # === Fallback Rule ===
    "Others": {
        "keywords": [],
        "request_type": "Others",
        "sub_request_type": "Others"
    }
}