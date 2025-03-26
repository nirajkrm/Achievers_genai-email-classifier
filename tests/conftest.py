import pytest

@pytest.fixture
def sample_email_text():
    """Shared test email content"""
    return """
    Subject: Repayment Notice
    Amount: USD 5,000,000.00
    Effective Date: 2023-12-01
    """