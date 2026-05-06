from fastapi import APIRouter
from . import HEALTH_PREFIX

router = APIRouter(prefix=HEALTH_PREFIX, tags=["Health"])


@router.get(
    "/", summary="Health check", description="Vérifie que l'API est opérationnelle."
)
def health_check() -> dict:
    """
    Endpoint de vérification de l'état de l'API.

    Returns:
        dict: statut de l'API
    """
    return {
        "status": "ok",
        "service": "gdelt-benin-api",
        "version": "1.0.0"
        }
