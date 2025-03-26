import sys
import os
import pytest
import pytest_asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from deduplicator import check_duplicate

@pytest_asyncio.fixture
async def clean_dedup_db():
    """Fixture to clean dedup database before each test"""
    from config import DEDUP_DB
    if os.path.exists(DEDUP_DB):
        os.remove(DEDUP_DB)
    yield
    if os.path.exists(DEDUP_DB):
        os.remove(DEDUP_DB)

@pytest.mark.asyncio
async def test_deduplication_unique(clean_dedup_db):
    result = await check_duplicate(
        email_id="email_123",
        cleaned_text="This is a unique email body.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert result["is_duplicate"] is False

@pytest.mark.asyncio
async def test_deduplication_repeat(clean_dedup_db):
    # First insertion
    await check_duplicate(
        email_id="email_repeat_1",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    
    # Second insertion
    result = await check_duplicate(
        email_id="email_repeat_2",
        cleaned_text="This email will be duplicated.",
        request_type="Others",
        date_str="2024-03-01"
    )
    assert result["is_duplicate"] is True