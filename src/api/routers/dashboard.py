from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

DESCRIPTION = """

Redirige vers le dashboard interactif basé sur Dash.

Ce endpoint ne sert pas directement une page HTML via FastAPI, mais effectue une redirection HTTP vers une application Dash exécutée en parallèle.

### Fonctionnement :

- FastAPI (port 8000) agit comme point d'entrée API
- Dash (port 8050) héberge le dashboard interactif
- Cette route redirige automatiquement l'utilisateur vers Dash

### Utilisation :

- Accéder à [/dashboard/dash](http://127.0.0.1:8050)
- L'utilisateur est redirigé vers `http://127.0.0.1:8050`

### Cas d'usage :

- Centraliser les accès via une seule API
- Intégrer facilement un frontend analytique (Dash)

### Prérequis :

- Le serveur Dash doit être lancé (automatiquement via FastAPI ou manuellement)

### Limitations :

- Swagger UI ne rend pas les redirections visuellement
- Il faut ouvrir l'URL dans un navigateur pour voir le dashboard

### Alternative :

Accès direct au dashboard : http://127.0.0.1:8050
"""

@router.get(
    "/dash",
    summary="Accès au dashboard interactif GDELT",
    description=DESCRIPTION,
    response_description="Redirection HTTP vers le dashboard Dash",)
async def streamlit_dashboard():
    """
    Redirige vers le dashboard Dash exécuté sur un port séparé.

    Returns:
        RedirectResponse: Redirection vers le serveur Dash (port 8050).
    """
    # Veuillez personnaliser le port de connection en fonction de votre machine.
    return RedirectResponse(url="http://127.0.0.1:8050")
