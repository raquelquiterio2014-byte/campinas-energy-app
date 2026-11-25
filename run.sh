#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export ERA_GPKG_PATH="${ERA_GPKG_PATH:-$(pwd)/backend/data/demo-network.gpkg}"
export ERA_STUDIES_DB_PATH="${ERA_STUDIES_DB_PATH:-$(pwd)/backend/data/demo-studies.db}"
python -m uvicorn app_server:app --host 127.0.0.1 --port 8000
