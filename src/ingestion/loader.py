from typing import List
import pandas as pd
from fastapi import HTTPException, status

from . import parse_gdelt_zip, apply_gdelt_schema


def load_gdelt_data(paths: List[str], data_type: str) -> pd.DataFrame:
    """
    Charge et agrège des fichiers GDELT (ZIP) en un DataFrame unique.

    Cette fonction :
    - lit plusieurs fichiers ZIP locaux
    - extrait les fichiers CSV internes
    - applique le schéma GDELT (colonnes nommées)
    - concatène les données en un seul DataFrame

    Args:
        paths (List[str]): Liste des chemins vers les fichiers ZIP.
        data_type (str): Type de données GDELT :
            - "event"
            - "gkg"
            - "mention"

    Returns:
        pd.DataFrame: DataFrame contenant toutes les données agrégées.

    Raises:
        HTTPException:
            - 400: type invalide ou chemin invalide
            - 404: aucun fichier valide trouvé
            - 422: données vides
            - 500: erreur interne

    Notes:
        - Les fichiers inexistants ou corrompus sont ignorés
        - Les erreurs de parsing sont loggées mais n'arrêtent pas le pipeline
        - Le schéma GDELT est appliqué automatiquement

    Example:
        >>> df = load_gdelt_data(paths, "event")
    """

    try:
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="paths doit être une liste de chaînes (chemins fichiers).",
            )

        if data_type not in {"event", "gkg", "mention"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="data_type invalide (event, gkg, mention).",
            )

        if len(paths) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun fichier fourni.",
            )

        merge_df = pd.DataFrame()
        processed_files = 0
        failed_files = []

        for path in paths:
            try:
                df = parse_gdelt_zip(path)

                if df.empty:
                    continue

                df = apply_gdelt_schema(df, data_type)

                merge_df = pd.concat([merge_df, df], ignore_index=True)
                processed_files += 1

            except Exception as e:
                failed_files.append({"file": path, "error": str(e)})
                continue

        if processed_files == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun fichier valide n'a pu être chargé.",
            )

        if merge_df.empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Les fichiers ont été lus mais aucune donnée exploitable.",
            )

        return merge_df

    except HTTPException:
        raise

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission refusée lors de l'accès aux fichiers.",
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Un ou plusieurs fichiers sont introuvables.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du chargement des données: {str(e)}",
        )
