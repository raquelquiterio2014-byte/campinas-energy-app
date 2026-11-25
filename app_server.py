"""ERA Energy App: independent frontend combined with the validated V7 API."""
import os
import sys
from pathlib import Path

from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent
BACKEND = HERE / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Absolute paths avoid dependency on the directory from which Uvicorn is invoked.
os.environ.setdefault("ERA_GPKG_PATH", str(BACKEND / "data" / "local-data.gpkg"))
os.environ.setdefault("ERA_STUDIES_DB_PATH", str(BACKEND / "data" / "studies.db"))

from app.main import app  # noqa: E402

app.mount("/app", StaticFiles(directory=HERE / "frontend", html=True), name="era-energy-app")
