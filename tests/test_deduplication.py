import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from deduplicator import check_duplicate

@pytest.mark.asyncio
async def test_deduplication_unique():
    result = await check_duplicate(
        email_id="email_123",
        cleaned_text="This is a unique email body.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert result["is_duplicate"] is False

@pytest.mark.asyncio
async def test_deduplication_repeat():
    _ = await check_duplicate(
        email_id="email_repeat_1",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    result = await check_duplicate(
        email_id="email_repeat_2",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert result["is_duplicate"] is True
