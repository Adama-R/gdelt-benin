# src/api/routers/analytics.py

import pandas as pd
from fastapi import APIRouter, HTTPException

from analysis.metrics import preprocess_gdelt, analyze_gdelt
from core.constants import GDELT_PREFIX, GDELT_BENIN, GDELT_ML_DATA

router = APIRouter(prefix=f"{GDELT_PREFIX}/analytics", tags=["Analytics"])


@router.get(
    GDELT_BENIN + "/analysis",
    summary="Analyse des données GDELT",
)
async def analyze_benin_data(
    # dataType: Literal["event", "gkg", "mention"] = "event",
) -> dict:
    """
    Analyse les données GDELT déjà traitées.
    """

    try:
        # À décommenter pour bénéficier de l'API.
        # path = f"data/processed/{dataType}/GDELT_ML_DATA"

        path = f"{GDELT_ML_DATA}"

        df = pd.read_csv(path)

        df = preprocess_gdelt(df)
        result = analyze_gdelt(df)

        return result

    except FileNotFoundError:
        raise HTTPException(404, "Fichier de données introuvable.")

    except Exception as e:
        raise HTTPException(500, f"Erreur analyse: {str(e)}")
