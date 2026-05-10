
import pytest
from fastapi import HTTPException

def test_generate_urls_event():
    from ingestion import generate_gdelt_urls

    urls = generate_gdelt_urls("20250101", "20250102", "event")

    assert len(urls) == 2
    assert "20250101" in urls[0]

def test_invalid_data_type():
    from ingestion import generate_gdelt_urls

    with pytest.raises(HTTPException):
        generate_gdelt_urls("20250101", "20250102", "invalid")

def test_generate_mentions_urls():
    from ingestion import generate_gdelt_urls

    urls = generate_gdelt_urls("20250101", "20250101", "mention")

    assert len(urls) == 96  # 24h * 4
