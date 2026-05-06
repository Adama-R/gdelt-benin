from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class FailedURL(BaseModel):
    url: str
    error: str

class PipelineResponse(BaseModel):
    """
    Réponse standard du pipeline GDELT.

    Cette réponse s'adapte selon le mode d'exécution :

    - save_data=True  → fichier CSV généré
    - save_data=False → données retournées en mémoire (preview)

    Attributes:
        rows_count (int): Nombre total de lignes traitées.
        processing_time_sec (float): Temps total du pipeline.
        failed (List[FailedSource]): Liste des sources ayant échoué.
        output_path (Optional[str]): Chemin du fichier CSV généré.
        data_preview (Optional[Dict]): Aperçu des données (si non sauvegardé).
    """
    rows_count: int
    processing_time_sec: float
    failed: List[FailedURL]

    output_path: Optional[str] = None
    data_preview: Optional[Dict[str, Any]] = None
    data_type: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rows_count": 12000,
                "processing_time_sec": 12.5,
                "failed": [],
                "output_path": "data/processed/event/data.csv",
                "data_preview": {
                    "Actor1Name": ["USA", "France"],
                    "EventCode": [20, 30]
                },
                "data_type": "event",
            }
        }
    )
