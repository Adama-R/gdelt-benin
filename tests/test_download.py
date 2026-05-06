import pytest
import httpx


@pytest.mark.asyncio
async def test_download_file_success():
    from ingestion import download_file_stream

    url = "http://data.gdeltproject.org/events/20240101.export.CSV.zip"

    content = await download_file_stream(url)

    assert isinstance(content, bytes)
    assert len(content) > 0


@pytest.mark.asyncio
async def test_download_file_invalid_url():
    from ingestion import download_file_stream

    url = "http://invalid-url/test.zip"

    with pytest.raises(Exception):
        await download_file_stream(url)


@pytest.mark.asyncio
async def test_client_connection():
    url = "http://data.gdeltproject.org/events/20250101.export.CSV.zip"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.status_code)
        assert r.status_code == 200
