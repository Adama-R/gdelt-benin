import pytest


@pytest.mark.asyncio
async def test_parse_gdelt_zip_success():
    from ingestion import download_file_stream
    from ingestion import parse_gdelt_zip

    url = "http://data.gdeltproject.org/events/20240101.export.CSV.zip"

    content = await download_file_stream(url)
    df = parse_gdelt_zip(content)

    assert df is not None
    assert len(df) > 0


@pytest.mark.asyncio
async def test_parse_invalid_zip():
    from ingestion import parse_gdelt_zip

    with pytest.raises(Exception):
        parse_gdelt_zip(b"not a zip")
