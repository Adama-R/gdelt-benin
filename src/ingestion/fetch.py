from pathlib import Path
from fastapi import HTTPException, status
from datetime import datetime, timedelta


def generate_gdelt_urls(start_date: str, end_date: str, data_type: str) -> list[str]:
    """
    Génère les URLs des fichiers GDELT (Events, GKG, Mentions) sur un intervalle de dates.

    Cette fonction construit dynamiquement les liens vers les fichiers compressés
    disponibles sur le serveur GDELT, en fonction du type de données demandé et
    de la plage de dates fournie.

    Args:
        start_date (str): Date de début au format 'YYYYMMDDHHMMSS'.
        end_date (str): Date de fin au format 'YYYYMMDDHHMMSS'.
        data_type (str): Type de données GDELT à récupérer.
            Valeurs autorisées :
                - "event"
                - "gkg"
                - "mention"

    Returns:
        List[str]: Liste des URLs des fichiers GDELT correspondants.

    Raises:
        HTTPException:
            - 400: Type de données invalide.
            - 422: Format de date invalide.
            - 422: Date de début > date de fin.

    Notes:
        - Les fichiers sont générés jour par jour.
        - La fonction ne vérifie pas si les fichiers existent réellement côté serveur.
        - GDELT peut ne pas avoir de données pour certaines dates.

    Example:
        >>> generate_gdelt_urls("20250101000000", "20250103000000", "event")
        [
            "http://data.gdeltproject.org/gdeltv2/20250101000000.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20250102000000.export.CSV.zip",
            "http://data.gdeltproject.org/gdeltv2/20250103000000.export.CSV.zip"
        ]
    """

    try:
        if not all(isinstance(x, str) for x in (start_date, end_date, data_type)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Les paramètres doivent être des chaînes de caractères.",
            )

        data_type = data_type.lower()

        base_urls: dict[str, str] = {
            "event": "http://data.gdeltproject.org/gdeltv2/",
            "gkg": "http://data.gdeltproject.org/gdeltv2/",
            "mention": "http://data.gdeltproject.org/gdeltv2/",
        }

        patterns: dict[str, str] = {
            "event": "{datetime}.export.CSV.zip",
            "gkg": "{datetime}.gkg.csv.zip",
            "mention": "{datetime}.mentions.CSV.zip",
        }

        if data_type not in base_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type de données invalide. Choisir parmi: event, gkg, mention.",
            )

        start = None
        end = None

        try:
            start = datetime.strptime(start_date, "%Y%m%d%H%M%S")
            end = datetime.strptime(end_date, "%Y%m%d%H%M%S")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Format de date invalide. Utiliser YYYYMMDDHHMMSS.",
            )

        if start > end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La date de début doit être inférieure à la date de fin.",
            )

        if (end - start).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Intervalle trop grand (max 1 an recommandé).",
            )

        urls: list[str] = []
        current: datetime = start

        while current <= end:
            # Arrondi des minutes à 0, 15, 30, 45
            minute = (current.minute // 15) * 15
            dt = current.replace(minute=minute, second=0)
            date_str = dt.strftime("%Y%m%d%H%M%S")
            urls.append(base_urls[data_type] + patterns[data_type].format(datetime=date_str))
            current += timedelta(minutes=15)
        return urls

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de la génération des URLs: {str(e)}",
        )


def generate_local_gdelt_paths(
    start_date: str,
    end_date: str,
    data_type: str,
    base_dir: str = "data/raw",
) -> list[str]:
    """
    Génère les chemins locaux des fichiers GDELT téléchargés.

    Cette fonction construit les chemins vers les fichiers ZIP stockés
    localement selon :
        data/raw/{data_type}/{date}.zip

    Args:
        start_date (str): Date de début au format 'YYYYMMDDHHMMSS'.
        end_date (str): Date de fin au format 'YYYYMMDDHHMMSS'.
        data_type (str): Type de données ('event', 'gkg', 'mention').
        base_dir (str): Répertoire racine des données.

    Returns:
        list[str]: Liste des chemins vers les fichiers ZIP existants.

    Raises:
        HTTPException:
            - 400: type invalide
            - 422: format de date invalide
            - 404: aucun fichier trouvé

    Notes:
        - Ne retourne QUE les fichiers existants
        - Ignore les fichiers absents
    """

    try:
        data_type = data_type.lower()

        if data_type not in {"event", "gkg", "mention"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type invalide: event, gkg, mention",
            )

        start = datetime()
        end = datetime()

        try:
            start = datetime.strptime(start_date, "%Y%m%d%H%M%S")
            end = datetime.strptime(end_date, "%Y%m%d%H%M%S")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Format date invalide (YYYYMMDDHHMMSS)",
            )

        if start > end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date > end_date",
            )

        base_path = Path(base_dir) / data_type

        if not base_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun dossier trouvé pour {data_type}",
            )

        paths = []
        current = start

        while current <= end:
            filename = current.strftime("%Y%m%d%H%M%S") + ".zip"
            file_path = base_path / filename

            if file_path.exists():
                paths.append(str(file_path))

            current += timedelta(days=1)

        if not paths:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun fichier local trouvé pour cette période",
            )

        return paths

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}",
        )
