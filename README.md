# GDELT Benin Analytics API

API de collecte, traitement et analyse des données du projet GDELT, avec un focus sur les événements liés au Bénin 🇧🇯.

---

## Objectif

Ce projet a été conçu dans le cadre du hackathon **iSHEERO 2026**.
Il permet de :

- Télécharger des données GDELT (format CSV compressé)
- Les traiter en mémoire (pipeline asynchrone)
- Nettoyer et filtrer les données (Bénin)
- Générer des statistiques exploitables
- Exposer les résultats via une API FastAPI

---

## Architecture du projet

```tree


gdelt-benin/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── raw/
│   │   ├── events/
│   │   │   ├── 20250101.zip
│   │   │   ├── 20250102.zip
│   │   │
│   │   ├── gkg/
│   │   │   ├── 20250101.zip
│   │   │
│   │   ├── mentions/
│   │   │   ├── 20250101.zip
│   │
│   ├── processed/
│   │   ├── events/
│   │   │   ├── events_clean.csv
│   │   │   ├── events_benin.csv
│   │   │
│   │   ├── gkg/
│   │   │   ├── gkg_clean.csv
│   │   │
│   │   ├── mentions/
│   │   │   ├── mentions_clean.csv
│   │   │
│   │   ├── merged/
│   │   │   ├── dataset_ml.csv   # dataset final
│   │
├── src/
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── fetch.py          # scrape GDELT
│   │   ├── download.py       # téléchargement async
│   │   ├── parse.py          # lecture zip -> DataFrame
│   │   └── pipeline.py       # orchestration ingestion
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   └── clean.py          # filtrage (Bénin)
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── metrics.py        # (analyse statistique)
│   │
│   ├── api/                  # api du backend
│   │   ├── __init__.py
│   │   ├── main.py           # point d’entrée FastAPI
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── gdelt.py      # routes GDELT
│   │   │   ├── analytics.py  # analytics check
│   │   │   └── health.py     # health check
│   │   │
│   │   └── dependencies.py   # injection dépendances
│   │
│   ├── core/                 # NOUVEAU
│   │   ├── __init__.py
│   │   └── constants.py      # routes, configs
│   │
│   ├── main.py               # script CLI (pipeline simple)
│
├── tests/
│   ├── test_fetch.py
│   ├── test_download.py
│   ├── test_parse.py
│   ├── test_filter.py
│   ├── test_pipeline.py
│
├── requirements/
│
├── pyproject.toml
├── README.md

```

## Pour tout exécution du projet

I. Entré les commandes suivante:

1. Rendez-vous dans le répertoire du projet

```bash

cd gdelt-benin


```

2. Créer un environnement de travail pour python

```bash

uv run venv


```

3. Vous installez les dépendences/packages du projet

```bash

uv sync --all-groups

```

4. Pour lancer le serveur backend

```bash

uv run uvicorn api.main:app --reload

```

5. Une fois le serveur backend lancer, rendez-vous dans votre navigateur sur le lien

```url

http://localhost:8000/docs
```

En fonction du point d'entré que vous voulez tester, vous avez seulement qu'à cliquer sur le bouton `Try it out`, car nous utilisons dans notre cas FastAPI comme serveur backend.

> Si vous voulez utiliser l'outil d'indexation de package python `pip`, vous pouvez suivre les étapes suivantes:

### Créer un environnement de travail python après clonage du projet

```bash

python -m venv .venv
```

### Activer l'environnement

- Windows :

powershell

```bash

.venv\Scripts\activate
```

- macOS / Linux :

bash

```bash

source .venv/bin/activate

```

Une fois activé, le nom de l'environnement, par exemple (.venv), devrait apparaître au début de la ligne de commande.

### Pour installer les dépences

```bash

pip install -r requirements.txt
```

### Désactiver l'environnement

Pour quitter l'environnement virtuel et revenir à l'installation Python globale, tapez simplement:

```bash

deactivate
```

> Pour ce projet nous avons utilisé ChatGPT pour aller plus vite dans nos recherches.
