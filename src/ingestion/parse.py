import pandas as pd
from ingestion.download import download_file_stream_on_local
from core.constants import (
    GDELT_EVENT_COLUMNS,
    GDELT_GKG_COLUMNS,
    GDELT_MENTION_COLUMNS,
)


def parse_gdelt_zip(filepath: str) -> pd.DataFrame:
    """
    Parse un fichier ZIP GDELT et retourne un DataFrame brut.

    Cette fonction est une couche d'abstraction qui délègue la lecture
    du fichier ZIP local à la fonction de téléchargement et extraction.

    Args:
        filepath (str): Chemin vers le fichier ZIP local.

    Returns:
        pd.DataFrame: Données brutes extraites du ZIP.

    Notes:
        - Cette fonction ne réalise aucun nettoyage.
        - Elle sert uniquement de point d'entrée du parsing.
    """
    return download_file_stream_on_local(filepath)


def apply_gdelt_schema(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """
    Applique un schéma de colonnes adapté au type de données GDELT.

    Cette fonction transforme un DataFrame brut issu des fichiers GDELT
    (colonnes indexées numériquement) en DataFrame structuré avec des noms
    de colonnes explicites selon le type de dataset.

    Args:
        df (pd.DataFrame): DataFrame brut issu du parsing ZIP GDELT.
        data_type (str): Type de données à traiter.
            Valeurs possibles :
                - "event" : événements politiques/sociaux
                - "gkg" : Global Knowledge Graph
                - "mention" : mentions médiatiques

    Returns:
        pd.DataFrame: DataFrame avec colonnes nommées selon le schéma GDELT.

    Notes:
        - Cette étape est essentielle pour rendre les données exploitables en ML.
        - Elle doit être exécutée avant tout filtrage ou analyse.
    """
    df = df.copy()

    if data_type == "event":
        df.columns = GDELT_EVENT_COLUMNS

    elif data_type == "gkg":
        df.columns = GDELT_GKG_COLUMNS

    elif data_type == "mention":
        df.columns = GDELT_MENTION_COLUMNS

    return df
