import pytest
import httpx
from unittest.mock import AsyncMock, patch

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

@pytest.mark.asyncio
async def test_download_file_success():
    from download import download_file_stream

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.aiter_bytes.return_value = [b"data"]
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.stream.return_value.__aenter__.return_value = mock_response

        result = await download_file_stream("http://test.com", "file", "event")

        assert "file.zip" in result
