import pytest


@pytest.mark.asyncio
async def test_parse_gdelt_zip_success():
    from ingestion import download_file_stream, parse_gdelt_zip

    url = "http://data.gdeltproject.org/gdeltv2/20250101000000.export.CSV.zip"

    filepath: str = await download_file_stream(url, "20250101000000", "event", True)
    df = parse_gdelt_zip(filepath)

    assert df is not None
    assert len(df) > 0


@pytest.mark.asyncio
async def test_parse_invalid_zip():
    from ingestion import parse_gdelt_zip

    with pytest.raises(Exception):
        parse_gdelt_zip(b"not a zip")

@pytest.mark.xfail
def test_apply_schema_event():
    import pandas as pd
    from ingestion import apply_gdelt_schema

    df = pd.DataFrame([[1,2,3]])

    with pytest.raises(ValueError):
        apply_gdelt_schema(df, "event")
