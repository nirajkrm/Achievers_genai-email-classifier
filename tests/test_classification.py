import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_classifier import rule_based_classification

def test_rule_based_fallback():
    subject = "Commitment Change - Upsize"
    body = "The borrower has increased the commitment amount."
    result = rule_based_classification(subject, body)

    assert isinstance(result, dict)
    assert result["request_type"] == "Commitment Change"
    assert result["sub_request_type"] == "Commitment Increase"
    assert result["priority"] == "Medium"
