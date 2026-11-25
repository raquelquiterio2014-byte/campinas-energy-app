from pathlib import Path
import os

def get_gpkg_path() -> Path:
    return Path(os.getenv("ERA_GPKG_PATH", "data/local-data.gpkg")).expanduser().resolve()

def get_studies_db_path() -> Path:
    return Path(os.getenv("ERA_STUDIES_DB_PATH", "data/studies.db")).expanduser().resolve()

def get_osm_tile_url() -> str:
    return os.getenv("ERA_OSM_TILE_URL", "https://tile.openstreetmap.org/{z}/{x}/{y}.png")
