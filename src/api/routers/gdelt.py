from typing import Literal, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime

from core.constants import GDELT_BENIN, GDELT_PREFIX
from api.schemas.gdelt import PipelineResponse
from ingestion.fetch import generate_gdelt_urls, generate_local_gdelt_paths
from ingestion.pipeline import process_gdelt_pipeline_to_csv
from ingestion.loader import load_gdelt_data
from ingestion.filter import link_mentions_to_events


router = APIRouter(prefix=GDELT_PREFIX, tags=["GDELT"])


@router.get(
    GDELT_BENIN + "/remote/data",
    response_model=PipelineResponse,
    summary="Récupérer les données GDELT pour le Bénin",
    description="Télécharge, parse et filtre les données GDELT (Events, GKG, Mentions).",
)
async def get_benin_data(
    start_date: str,
    end_date: str,
    dataType: Literal["event", "gkg", "mention"] = "event",
    save_data: bool = True,
)-> Any:
    """
    Pipeline complet de récupération et traitement des données GDELT pour le Bénin.

    Cet endpoint orchestre l'ensemble du flux de données GDELT :
    1. Génération des URLs GDELT (Events, GKG ou Mentions) selon une plage de dates
    2. Téléchargement et parsing des fichiers distants
    3. Filtrage des données liées au Bénin
    4. Agrégation des résultats dans un DataFrame unique
    5. Sauvegarde optionnelle des données traitées sur disque

    Args:
        start_date (str): Date de début au format 'YYYYMMDD'.
        end_date (str): Date de fin au format 'YYYYMMDD'.
        dataType (Literal["event", "gkg", "mention"]):
            Type de données GDELT à traiter :
            - event : événements politiques/sociaux
            - gkg : contexte sémantique global
            - mention : citations et références médiatiques
        save_data (bool): Si True, sauvegarde les fichiers téléchargés localement.

    Returns:
        dict: Résumé du traitement contenant :
            - rows_count (int): nombre total de lignes après agrégation
            - columns (list[str]): colonnes du DataFrame final
            - processing_time_sec (float): durée totale du pipeline
            - failed_urls (list[dict]): URLs ayant échoué avec erreur associée
            - data_type (str): type de données traitées

    Raises:
        HTTPException:
            - 404: aucune URL générée ou aucune donnée valide récupérée
            - 403: erreur de permission lors de l'écriture disque
            - 500: erreur interne inattendue

    Notes:
        - Ce endpoint est coûteux en ressources (multi-téléchargements HTTP)
        - Les données GDELT peuvent être volumineuses selon la période choisie
        - Les URLs invalides ou absentes sont ignorées et tracées dans "failed_urls"
    """
    start = datetime.now()

    urls = generate_gdelt_urls(start_date, end_date, dataType)

    output_path = (
        Path(f"data/processed/{dataType}/data.csv") if save_data else None
    )

    df, total_rows, failed = await process_gdelt_pipeline_to_csv(
        urls,
        dataType,
        "remote",
        save_data,
        output_path,
    )

    if dataType == "mention":

        events_df = load_gdelt_data(
            generate_local_gdelt_paths(start_date, end_date, "event"),
            "event",
        )

        if save_data:
            mentions_df = pd.read_csv(output_path)
        else:
            mentions_df = df

        mentions_df = link_mentions_to_events(
            mentions_df, events_df, "BN"
        )

        total_rows = len(mentions_df)

        if save_data:
            mentions_df.to_csv(output_path, index=False)
        else:
            df = mentions_df

    end = datetime.now()

    return PipelineResponse(
        rows_count=total_rows,
        processing_time_sec=(end - start).total_seconds(),
        failed=failed,
        output_path=str(output_path) if save_data else None,
        data_preview=None if save_data else df.head().to_dict())

@router.get(
    GDELT_BENIN + "/local/data",
    response_model=PipelineResponse,
    summary="Traitement local des données GDELT",
    description="Lit les fichiers ZIP locaux et applique le pipeline GDELT complet.",
)
async def get_benin_data_local(
    start_date: str,
    end_date: str,
    dataType: Literal["event", "gkg", "mention"] = "event",
    save_data: bool = True,
) -> PipelineResponse:
    start = datetime.now()

    paths = generate_local_gdelt_paths(start_date, end_date, dataType)

    if not paths:
        raise HTTPException(404, "Aucun fichier local trouvé.")
        output_path = (
        Path(f"data/processed/{dataType}/data.csv")
        if save_data
        else None
    )

    _, total_rows, failed = await process_gdelt_pipeline_to_csv(
        sources=paths,
        data_type=dataType,
        source_type="local",
        save_data=save_data,
        output_path=output_path,
    )

    if dataType == "mention":

        events_paths = generate_local_gdelt_paths(
            start_date, end_date, "event"
        )

        events_df = load_gdelt_data(events_paths, "event")

        mentions_df = load_gdelt_data(paths, "mention")

        mentions_df = link_mentions_to_events(
            mentions_df, events_df, "BN"
        )

        if save_data:
            mentions_df.to_csv(output_path, index=False)

        total_rows = len(mentions_df)

    end = datetime.now()

    return PipelineResponse(
        rows_count=total_rows,
        processing_time_sec=(end - start).total_seconds(),
        failed=failed,
        output_path=str(output_path) if save_data else None,
        data_preview=None if save_data else mentions_df.head().to_dict(),
        data_type=dataType)
