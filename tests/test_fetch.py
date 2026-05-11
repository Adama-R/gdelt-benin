
import pytest
from fastapi import HTTPException

def test_generate_urls_event():
    from ingestion import generate_gdelt_urls

    urls: list[str] = generate_gdelt_urls("20250101000000", "20250102000000", "event")

    assert len(urls) == 97
    assert "20250101000000" in urls[0]

def test_invalid_data_type():
    from ingestion import generate_gdelt_urls

    with pytest.raises(HTTPException):
        generate_gdelt_urls("20250101", "20250102", "invalid")

def test_generate_mentions_urls():
    from ingestion import generate_gdelt_urls

    urls: list[str] = generate_gdelt_urls("20250101000000", "20250101080400", "mention")

    assert len(urls) == 33

def test_generate_gkg_urls():
    from ingestion import generate_gdelt_urls

    urls: list[str] = generate_gdelt_urls("20250101000000", "20250101090000", "mention")

    assert len(urls) == 37
