import pytest


@pytest.mark.asyncio
async def test_fetch_and_parse():
    from ingestion import fetch_and_parse

    url = "http://data.gdeltproject.org/gdeltv2/20250101000000.export.CSV.zip"

    df = await fetch_and_parse(url, 'event')

    assert df is not None
    assert len(df) > 0
