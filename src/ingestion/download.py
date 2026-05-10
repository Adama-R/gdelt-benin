import httpx
import pandas as pd
import zipfile
import aiofiles
from pathlib import Path
from fastapi import HTTPException, status
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=5),
    retry=retry_if_exception_type(
        (
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.ConnectTimeout,
            httpx.RemoteProtocolError,
        )
    ),
)
async def download_file_stream(url: str, filename: str, data_type: str, save_data: bool = True) -> str:
    """
    Télécharge un fichier GDELT distant (ZIP) de manière asynchrone
    et l'enregistre localement selon son type.

    Cette fonction :
    - télécharge un fichier via streaming HTTP
    - applique un mécanisme de retry automatique (tenacity)
    - sauvegarde le fichier dans un dossier structuré par type :
        data/raw/{data_type}/

    Args:
        url (str): URL du fichier à télécharger.
        filename (str): Nom du fichier de sortie (sans extension).
        data_type (str): Type de données GDELT :
            - "event"
            - "gkg"
            - "mention"

    Returns:
        str: Chemin local du fichier ZIP sauvegardé.

    Raises:
        HTTPException:
            - 400: URL invalide ou erreur HTTP client
            - 404: fichier introuvable
            - 502: erreur serveur distant
            - 503: service indisponible après retries
            - 504: timeout
            - 500: erreur interne

    Notes:
        - Les fichiers sont stockés dans :
            data/raw/{data_type}/{filename}.zip
        - Le dossier est créé automatiquement si inexistant.
        - Le téléchargement se fait en streaming pour éviter
          de charger tout le fichier en mémoire.
    """
    try:

        output_path = Path()

        if save_data:
            base_path = Path(f"data/raw/{data_type}")
            base_path.mkdir(parents=True, exist_ok=True)

            output_path = base_path / f"{filename}.zip"

        async with httpx.AsyncClient(
            timeout=60.0, headers={"User-Agent": "Mozilla/5.0"}
        ) as client:
            async with client.stream("GET", url) as response:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 404:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Fichier introuvable à l'URL fournie.",
                        )
                    elif exc.response.status_code >= 500:
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Erreur serveur distant.",
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Erreur HTTP: {exc.response.status_code}",
                        )

                if save_data:
                    async with aiofiles.open(output_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            await f.write(chunk)

        return str(output_path)

    except httpx.InvalidURL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="URL invalide."
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout lors du téléchargement.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service distant indisponible après plusieurs tentatives.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}",
        )


def download_file_stream_on_local(zipFile: str) -> pd.DataFrame:
    """
    Lit un fichier ZIP GDELT local et retourne un DataFrame pandas.

    Supporte :
        - Events
        - GKG
        - Mentions

    Args:
        zipFile (str): chemin du fichier ZIP local

    Returns:
        pd.DataFrame: données concaténées du ZIP

    Raises:
        HTTPException:
            - 404: fichier introuvable
            - 400: fichier corrompu ou invalide
            - 500: erreur interne
    """

    try:
        zip_file_path = Path(zipFile)

        if not zip_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fichier ZIP introuvable.",
            )

        if zip_file_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le chemin fourni est un dossier, pas un fichier ZIP.",
            )

        dfs = []

        with zipfile.ZipFile(zip_file_path) as zf:
            file_list = zf.namelist()

            for f in file_list:
                if not f.lower().endswith(".csv"):
                    continue

                try:
                    with zf.open(f) as file:
                        df = pd.read_csv(
                            file, sep="\t", low_memory=False, encoding_errors="ignore"
                        )

                        if df.empty:
                            continue

                        dfs.append(df)

                except pd.errors.EmptyDataError:
                    continue

                except pd.errors.ParserError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Erreur parsing CSV: {f}",
                    )

                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Erreur encodage fichier: {f}",
                    )

        if not dfs:
            return pd.DataFrame()

        merge_df = pd.concat(dfs, ignore_index=True)

        return merge_df

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier ZIP corrompu ou invalide.",
        )

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission refusée pour accéder au fichier.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}",
        )
