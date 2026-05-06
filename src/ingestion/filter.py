import pandas as pd
from fastapi import HTTPException, status

def link_mentions_to_events(
    mentions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    country_code: str = "BN",
) -> pd.DataFrame:
    """
    Relie les données GDELT Mentions aux Events afin de filtrer
    les mentions associées à un pays donné.

    Cette fonction permet d'extraire les mentions médiatiques liées
    à des événements localisés dans un pays spécifique (ex: Bénin).

    Le lien entre les deux datasets se fait via la colonne :
        - GLOBALEVENTID

    Étapes du traitement :
        1. Filtrer les événements selon le pays cible
        2. Extraire les identifiants d'événements
        3. Filtrer les mentions correspondantes via une jointure

    Args:
        mentions_df (pd.DataFrame): DataFrame contenant les données Mentions.
        events_df (pd.DataFrame): DataFrame contenant les données Events.
        country_code (str): Code pays ISO (ex: "BN" pour le Bénin).

    Returns:
        pd.DataFrame:
            DataFrame contenant uniquement les mentions associées
            aux événements du pays spécifié.

    Raises:
        HTTPException:
            - 400: colonnes requises absentes
            - 404: aucune donnée trouvée après filtrage
            - 422: DataFrame vide
            - 500: erreur interne

    Notes:
        - Les DataFrames doivent contenir la colonne "GLOBALEVENTID"
        - events_df doit contenir "ActionGeo_CountryCode"
        - Les deux datasets doivent couvrir la même période temporelle

    Example:
        >>> link_mentions_to_events(mentions_df, events_df, "BN")
    """

    try:
        if not all(isinstance(x, pd.DataFrame) for x in (mentions_df, events_df)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les entrées doivent être des DataFrames pandas.",
            )

        if not isinstance(country_code, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le paramètre country_code doivent être une chaînes de caractères.",
            )

        if mentions_df.empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le DataFrame Mentions est vide.",
            )

        if events_df.empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Le DataFrame Events est vide.",
            )

        required_event_cols = {"GLOBALEVENTID", "ActionGeo_CountryCode"}
        required_mention_cols = {"GLOBALEVENTID"}

        if not required_event_cols.issubset(events_df.columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Colonnes manquantes dans Events: {required_event_cols}",
            )

        if not required_mention_cols.issubset(mentions_df.columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Colonne 'GLOBALEVENTID' absente dans Mentions.",
            )

        filtered_events = events_df[
            events_df["ActionGeo_CountryCode"] == country_code
        ]

        if filtered_events.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun événement trouvé pour le pays {country_code}.",
            )

        result_df = mentions_df.merge(
            filtered_events[["GLOBALEVENTID"]],
            on="GLOBALEVENTID",
            how="inner",
        )

        if result_df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucune mention correspondante trouvée après jointure.",
            )

        return result_df

    except HTTPException:
        raise

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colonne introuvable: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du linking Mentions-Events: {str(e)}",
        )
