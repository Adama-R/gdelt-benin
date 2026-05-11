import pandas as pd
from typing import Optional
from pathlib import Path
from fastapi import HTTPException

from ingestion.parse import apply_gdelt_schema, parse_gdelt_zip
from ingestion.download import download_file_stream, download_file_stream_on_local
from processing.clean import filter_benin

async def fetch_and_parse(
    url_zipPath: str, data_type: str, save: bool = True
) -> pd.DataFrame:
    """
    Télécharge un fichier GDELT (zip) et retourne un DataFrame pandas.

    Args:
        url (str): URL du fichier GDELT
        data_type (str): Type de données GDELT :
            - "event"
            - "gkg"
            - "mention"
        save(bool): Sauvegarde des données en local, false par défaux

    Returns:
        pd.DataFrame: données chargées
    """

    if save:
        filename = url_zipPath.split("/")[-1].split(".")[0]
        content = await download_file_stream(url_zipPath, filename, data_type)
        return parse_gdelt_zip(content)

    return download_file_stream_on_local(url_zipPath)

async def process_gdelt_pipeline_to_csv(
    sources: list[str],
    data_type: str,
    source_type: str,
    save_data: bool = False,
    output_path: Optional[Path] = None,
) -> tuple[Optional[pd.DataFrame], int, list]:
    """
    Pipeline GDELT avec option d'écriture disque.

    Si save_data=False → retourne uniquement le DataFrame
    Si save_data=True  → écrit en CSV + retourne stats

    Returns:
        (df | None, total_rows, failed)
    """

    merge_df = pd.DataFrame()
    total_rows = 0
    failed = []

    if save_data:
        if output_path is None:
            raise HTTPException(400, "output_path requis si save_data=True")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.exists():
                output_path.unlink()

        except PermissionError:
            raise HTTPException(403, "Permission refusée pour créer le dossier")

        except OSError as e:
            raise HTTPException(500, f"Erreur filesystem: {str(e)}")

        header_written = False

    for src in sources:
        try:
            if source_type == "remote":
                df = await fetch_and_parse(src, data_type, save_data)
            else:
                df = parse_gdelt_zip(src)

            if df.empty:
                continue

            df = apply_gdelt_schema(df, data_type)

            if data_type in ["event", "gkg"]:
                df = filter_benin(df, data_type)

            if df.empty:
                continue

            if save_data:
                try:
                    df.to_csv(
                        output_path,
                        mode="a",
                        index=False,
                        header=not header_written,
                    )
                    header_written = True

                except PermissionError:
                    raise HTTPException(403, "Écriture refusée")

                except OSError as e:
                    raise HTTPException(500, f"Erreur écriture: {str(e)}")

            else:
                merge_df = pd.concat([merge_df, df], ignore_index=True)

            total_rows += len(df)

        except Exception as e:
            failed.append({"source": src, "error": str(e)})

    if total_rows == 0:
        raise HTTPException(404, "Aucune donnée traitée.")

    return (None if save_data else merge_df, total_rows, failed)
