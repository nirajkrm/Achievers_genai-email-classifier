# GenAI-Powered Email Classifier for Financial Operations | OCR + GPT + IMAP + Webhook Ready



-----------------------------
### Overview

This project is a **Generative AI-powered Email Classification and OCR solution** designed to automate the processing of financial servicing emails. It leverages **Large Language Models (LLMs)** to classify emails, extract key fields, detect duplicates, and generate structured outputs for integration into loan servicing workflows. The solution is built to handle diverse email formats, including attachments, and is scalable for high-volume processing.


-----------------------------
### Key Features

  1. **Email Classification**
     - Classifies emails into predefined **Request Types** and **Sub-Request Types** based on sender's intent.
     - Uses OpenAI's GPT models for context-aware classification.
     - Supports multi-intent emails, identifies the **primary intent**, **confidence**, and **reasoning**.

  2. **Context-Based Field Extraction**
     - Extracts fields like **deal name**, **amount**, **dates**, etc., from body and attachments.
     - Supports `.eml`, `.pdf`, `.docx`, `.txt`, and image-based attachments using OCR.

  3. **Duplicate Email Detection**
     - Detects duplicates via content hashing and context-aware analysis.
     - Adds explanation for flagged duplicates.

  4. **Webhook Integration (Optional)**
     - Sends processed JSON output to external systems (e.g., ticketing tools, backends) via HTTP POST.

  5. **IMAP Inbox Integration (Optional)**
     - Monitors Outlook/IMAP email inbox.
     - Auto-fetches and processes new unread emails.

  6. **Streamlit GUI (Optional)**
     - Clean, pastel-themed interface for file upload and live classification.
     - Displays output and allows downloads.

  7. **Async-Powered Pipeline**
     - Built with `asyncio` for concurrent email processing and maximum throughput.

  8. **Rotating Logs**
     - Logs every run to `logs/pipeline.log`, rotates every 2 days (5 backups retained).
     - Logs both to console and file using `TimedRotatingFileHandler`.

---------------------------
### Installation

  ### Prerequisites

   - Python 3.8 or higher
   - Tesseract OCR installed and added to PATH
   - Valid OpenAI API Key
   - Internet access

  ### Setup Steps

  1. **Clone the repository**

    git clone <repository-url>
    cd <repository-folder>

  2. **Install all dependencies**

    pip install -r requirements.txt

  3. **Install Tesseract OCR**

    - Download and install from: https://github.com/tesseract-ocr/tesseract/wiki
    - Add the install path to your system PATH  
      Example: C:\Program Files\Tesseract-OCR

  4. **Create a `.env` file**

    	OPENAI_API_KEY=sk-xxxxxx  
    	EMAIL_HOST=outlook.office365.com  
    	EMAIL_USER=you@company.com  
    	EMAIL_PASS=your_password  
    	WEBHOOK_URL=https://your-ticketing-endpoint.com/api 
 

  5. **Verify Tesseract is working**

    tesseract --version


-----------------------
### Folder Structure

    project_root/
    │
    ├── orchestrator.py         # Main processing logic (CLI entrypoint)
    ├── config.py               # Loads .env variables
    ├── logger.py               # Rotating file + console logger
    ├── webhook_sender.py       # POSTs results to external endpoint
    ├── imap_watcher.py         # Optional IMAP-based email fetcher
    ├── streamlit_app.py        # Optional GUI
    │
    ├── email_loader.py
    ├── llm_classifier.py
    ├── field_extractor.py
    ├── cleaner.py
    ├── deduplicator.py
    │
    ├── data/
    │   ├── inputs/             # Drop your test files here
    │   └── outputs/            # Processed JSONs saved here
    │
    ├── logs/                   # Auto-generated logs
    │
    ├── tests/
    │   ├── test_classification.py
    │   ├── test_deduplication.py
    │   └── test_field_extraction.py
    │
    ├── .env                    # Your credentials and config (excluded from Git)
    ├── requirements.txt
    └── README.md


------------------
### How to Use

  ### A. Run From Command Line

       python orchestrator.py

  - Place your files in `data/inputs/`
  - Results will be saved in `data/outputs/`
  - Each output is also sent to your configured webhook (if set)

  ### B. Run as Web GUI (Optional)

    streamlit run streamlit_app.py

  - Drag and drop files in the interface
  - Results are visualized and downloadable

  ### C. Auto-Poll IMAP Inbox (Optional)

       python imap_watcher.py

- Automatically fetches new unread emails from configured inbox


--------------
### Sample Output (JSON)

    {
  "email_id": "sample_email",
  "subject": "Repayment Advice",
  "from": "bank@example.com",
  "to": "WELLS FARGO BANK",
  "date": "2025-02-04",
  "primary_request": {
    "request_type": "Money Movement - Outbound",
    "sub_request_type": "Principal Repayment",
    "primary_intent": "Loan repayment confirmation",
    "priority": "High",
    "confidence": 96,
    "reasoning": "The email contains principal repayment instructions and an urgent effective date."
  },
  "secondary_requests": [],
  "extracted_fields": {
    "amounts": [
      {
        "amount": 20000000.0,
        "currency": "USD",
        "tag": "repayment_amount"
      }
    ],
    "dates": ["2025-02-04", "2025-02-05"],
    "names": ["CANTOR FITZGERALD LP", "WELLS FARGO BANK"],
    "deal_name": "CANTOR FITZGERALD LP USD 425MM",
    "deal_cusip": "13861EAE0",
    "facility_cusip": "13861EAF7",
    "deal_isin": "US13861EAE05",
    "facility_isin": "US13861EAF79"
  },
  "duplication": {
    "is_duplicate": false,
    "duplicate_type": null,
    "matched_with": null,
    "reason": "No match with existing hash or content"
  }
}





-----------------------
### Testing

Run all tests with:

	pytest tests


Requires: pytest, pytest-asyncio 

	Installs: pip install pytest pytest-asyncio



----------------
### FUTURE POTENTIAL

While the core system is functional and ready for real use cases, the following features are provisioned or partially supported in the architecture and can be added easily:

• Support for `.xlsx` attachments (via pandas or openpyxl)
• Table extraction from PDFs and Word docs
• Real-time email push via webhook or Microsoft Graph API
• Prioritization or escalation based on intent confidence
• Admin dashboard to monitor queue and outputs
• Output delivery to SharePoint, FTP, or AWS S3
• Authentication support for secured GUI access
• Pre-built integrations with ServiceNow, JIRA, Freshdesk
• Auto-response to user with status or tracking ID
• Integration with LLM feedback loop to improve accuracy


--------------
### Troubleshooting

| Issue                        | Solution                                      |
|-----------------------------|-----------------------------------------------|
| Classification fails        | Verify OpenAI API key and internet            |
| No text from PDF            | Check OCR and PyMuPDF installed               |
| Output not generated        | Confirm input files exist in `data/inputs/`   |
| IMAP inbox fetch fails      | Validate `.env` email credentials             |
| Webhook error               | Check endpoint is reachable and valid         |
| Logs not saving             | Ensure `logs/` directory exists or is writable|


--------------
### License

Free to use for research, demo, or hackathon purposes. Attribution appreciated.

