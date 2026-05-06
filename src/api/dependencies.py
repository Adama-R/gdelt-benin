# src/api/dependencies.py

# from typing import Annotated
# from fastapi import Depends


def get_default_url() -> str:
    """
    Fournit une URL GDELT par défaut.

    Returns:
        str: URL GDELT
    """
    return "http://data.gdeltproject.org/events/20250101.export.CSV.zip"
