import pandas as pd


def preprocess_gdelt(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prétraitement des données GDELT.

    Cette fonction prépare un DataFrame brut GDELT pour l'analyse en :
    - convertissant la date GDELT (SQLDATE) en datetime
    - normalisant les colonnes numériques (tone, impact)
    - garantissant une copie indépendante du DataFrame

    Args:
        df (pd.DataFrame): DataFrame brut issu des données GDELT.

    Returns:
        pd.DataFrame: DataFrame enrichi avec :
            - date (datetime)
            - tone (float)
            - impact (float)

    Notes:
        - Les valeurs invalides sont converties en NaT / NaN
        - Compatible avec Event, GKG et Mention après schéma standardisé
        - Ne modifie pas le DataFrame original (copy défensive)
    """
    df = df.copy()

    df["date"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d", errors="coerce")
    df["tone"] = pd.to_numeric(df["AvgTone"], errors="coerce")
    df["impact"] = pd.to_numeric(df["GoldsteinScale"], errors="coerce")

    return df


def analyze_gdelt(df: pd.DataFrame) -> dict:
    """
    Analyse statistique descriptive des données GDELT.

    Cette fonction produit un résumé global des événements GDELT incluant :
    - volume total d'événements
    - évolution temporelle
    - principaux acteurs
    - types d'événements
    - statistiques de tonalité (tone)

    Args:
        df (pd.DataFrame): DataFrame GDELT prétraité (après preprocess_gdelt).

    Returns:
        dict: Dictionnaire contenant les métriques suivantes :

            total_events (int):
                Nombre total d'événements.

            events_over_time (dict):
                Nombre d'événements par date.

            top_actors (dict):
                Top 10 des acteurs les plus fréquents.

            event_types (dict):
                Top 10 des codes d'événements.

            tone (dict):
                Statistiques sur la tonalité :
                    - mean (float)
                    - min (float)
                    - max (float)

    Notes:
        - Les colonnes doivent exister dans le DataFrame pour être analysées
        - Les champs manquants retournent des structures vides ou None
        - Fonction adaptée pour API analytics ou dashboard
    """

    result = {}

    result["total_events"] = len(df)

    if "date" in df:
        timeline = (
            df.groupby(df["date"].dt.date)
            .size()
            .reset_index(name="count")
            .sort_values("date")
        )

        result["events_over_time"] = timeline.to_dict(orient="records")
    else:
        result["events_over_time"] = []

    if "Actor1Name" in df:
        actors = df["Actor1Name"].value_counts().head(10).reset_index()
        actors.columns = ["actor", "count"]

        result["top_actors"] = actors.to_dict(orient="records")
    else:
        result["top_actors"] = []

    if "EventCode" in df:
        events = df["EventCode"].value_counts().head(10).reset_index()
        events.columns = ["event_type", "count"]

        result["event_types"] = events.to_dict(orient="records")
    else:
        result["event_types"] = []

    # Tone
    if "tone" in df:
        result["tone"] = {
            "mean": float(df["tone"].mean()),
            "min": float(df["tone"].min()),
            "max": float(df["tone"].max()),
        }
    else:
        result["tone"] = None

    return result
