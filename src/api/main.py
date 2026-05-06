import os
import sys
import subprocess
from fastapi import FastAPI
from pathlib import Path

from .routers import gdelt, health, analytics
from .routers.dashboard import router as dashboard_router

app = FastAPI(title="GDELT Benin API")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dash_file = BASE_DIR / "dashboard" / "app.py"

dash_process = None

@app.on_event("startup")
def start_dash():
    global dash_process

    # Empêche double lancement avec reload
    if os.environ.get("RUN_MAIN") == "true":
        return

    dash_process = subprocess.Popen([
        sys.executable,
        str(dash_file)
    ])

@app.on_event("shutdown")
def shutdown():
    global dash_process
    if dash_process:
        dash_process.terminate()

app.include_router(health.router)
app.include_router(gdelt.router)
app.include_router(analytics.router)
app.include_router(dashboard_router)


if __name__ == "__main__":

    import uvicorn
    uvicorn.run("src.main:app", reload=True)
