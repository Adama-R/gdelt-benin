import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Configuration globale du projet.
    """

    GDELT_BASE_URL: str = os.getenv(
        "GDELT_BASE_URL",
        "http://data.gdeltproject.org/events/",
    )

    DEFAULT_DATE: str = os.getenv("DEFAULT_DATE", "20250101")

    SAVE_DATA: bool = os.getenv("SAVE_DATA", "false").lower() == "true"


settings = Settings()
