import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import TEAM_MAP, SUBJECT_RULES

def test_team_mapping():
    """Verify critical team mappings exist"""
    assert "Loan Repayment" in TEAM_MAP
    assert "Commitment Change" in TEAM_MAP
    assert TEAM_MAP.get("Others") == "General Servicing Team"

def test_subject_rules():
    """Verify fallback rules exist"""
    assert "commitment" in SUBJECT_RULES
    assert "repayment" in SUBJECT_RULES