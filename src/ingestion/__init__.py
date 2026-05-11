# src/ingestion/__init__.py

from ingestion.fetch import generate_gdelt_urls
from ingestion.filter import link_mentions_to_events
from ingestion.download import download_file_stream, download_file_stream_on_local
from ingestion.parse import parse_gdelt_zip, apply_gdelt_schema
from ingestion.pipeline import fetch_and_parse, process_gdelt_pipeline_to_csv
from ingestion.loader import load_gdelt_data
from processing.clean import filter_benin
from core.constants import (
    GDELT_EVENT_COLUMNS,
    GDELT_GKG_COLUMNS,
    GDELT_MENTION_COLUMNS,
)

__all__: list[str] = [
    "filter_benin",
    "generate_gdelt_urls",
    "link_mentions_to_events",
    "download_file_stream",
    "download_file_stream_on_local",
    "parse_gdelt_zip",
    "fetch_and_parse",
    "process_gdelt_pipeline_to_csv",
    "GDELT_EVENT_COLUMNS",
    "GDELT_GKG_COLUMNS",
    "GDELT_MENTION_COLUMNS",
    "apply_gdelt_schema",
    "load_gdelt_data"
]
