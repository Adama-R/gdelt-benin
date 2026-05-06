import pytest


@pytest.mark.asyncio
async def test_fetch_and_parse():
    from ingestion import fetch_and_parse

    url = "http://data.gdeltproject.org/events/20240101.export.CSV.zip"

    df = await fetch_and_parse(url)

    assert df is not None
    assert len(df) > 0
