import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_download_file_success():
    from ingestion import download_file_stream

    url = "http://data.gdeltproject.org/gdeltv2/20250101000000.export.CSV.zip"

    content = await download_file_stream(url, 20250101000000, "event", True)

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
    url = "http://data.gdeltproject.org/gdeltv2/20250101000000.export.CSV.zip"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.status_code)
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_download_file_success():
    from ingestion import download_file_stream

    with patch("httpx.AsyncClient") as mock_client:

        # Réponse HTTP mockée
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        async def mock_aiter_bytes():
            yield b"data"

        mock_response.aiter_bytes = mock_aiter_bytes

        # Context manager async pour stream()
        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__.return_value = mock_response
        mock_stream_context.__aexit__.return_value = None

        # Client HTTP mocké
        mock_client_instance = MagicMock()
        mock_client_instance.stream.return_value = mock_stream_context

        # AsyncClient() context manager
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await download_file_stream(
            "http://test.com",
            "file",
            "event"
        )

        assert result.endswith("file.zip")
