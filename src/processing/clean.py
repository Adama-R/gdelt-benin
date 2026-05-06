import pandas as pd

def filter_benin(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """
    Filtre les données GDELT pour ne conserver que les événements liés au Bénin.

    Cette fonction sélectionne uniquement les lignes dont le code pays
    correspond au Bénin (BN), basé sur la colonne ActionGeo_CountryCode.

    Args:
        df (pd.DataFrame): DataFrame GDELT structuré avec colonnes nommées.

    Returns:
        pd.DataFrame: DataFrame filtré contenant uniquement les événements du Bénin.

    Notes:
        - Nécessite que le schéma GDELT ait été appliqué avant utilisation.
        - Permet de réduire le volume de données pour analyse locale.
    """
    if data_type == "event":
        return df[df["ActionGeo_CountryCode"] == "BN"]

    elif data_type == "gkg":
        return df[df["V2Locations"].str.contains("BN", na=False)]

    elif data_type == "mention":
        raise ValueError(
            "Le filtrage des mentions nécessite les données Events. "
            "Utiliser 'link_mentions_to_events'."
        )

    else:
        raise ValueError(f"Type inconnu: {data_type}")
