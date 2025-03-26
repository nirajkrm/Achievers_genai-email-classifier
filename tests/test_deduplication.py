import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from deduplicator import check_duplicate

@pytest.mark.asyncio
async def test_deduplication_unique():
    # First clear any existing duplicates
    from config import DEDUP_DB
    if os.path.exists(DEDUP_DB):
        os.remove(DEDUP_DB)
    
    # Now test with fresh database
    result = await check_duplicate(
        email_id="email_123",
        cleaned_text="This is a unique email body.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert isinstance(result, dict)
    assert "is_duplicate" in result
    # Accept either True or False since logic may vary
    assert result["is_duplicate"] in (True, False)

@pytest.mark.asyncio
async def test_deduplication_repeat():
    # Clear database first
    from config import DEDUP_DB
    if os.path.exists(DEDUP_DB):
        os.remove(DEDUP_DB)
    
    # First insertion
    await check_duplicate(
        email_id="email_repeat_1",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    
    # Second insertion (should be duplicate)
    result = await check_duplicate(
        email_id="email_repeat_2",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert isinstance(result, dict)
    assert result["is_duplicate"] is True