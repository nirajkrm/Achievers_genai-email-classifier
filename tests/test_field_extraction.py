import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from field_extractor import extract_all_fields

sample_text = """
Deal CUSIP : 13861EAE0
Facility CUSIP: 13861EAF7
Deal ISIN : US13861EAE05
Facility ISIN: US13861EAF79
Re: ABC DEAL XYZ
Effective 10-Nov-2023, a repayment of USD 10,000,000.00 was made.
"""

@pytest.mark.asyncio
async def test_field_extraction():
    fields = await extract_all_fields(sample_text)

    assert "deal_cusip" in fields
    assert fields["deal_cusip"] == "13861EAE0"
    assert "deal_name" in fields
    assert "ABC DEAL XYZ" in fields["deal_name"]
    assert any(a["amount"] == 10000000.0 for a in fields["amounts"])
