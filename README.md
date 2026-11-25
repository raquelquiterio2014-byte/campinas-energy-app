# Campinas Energy App

Independent geospatial application using **fictional distribution-network scenarios** for interactive spatial analysis and persistent study management.

## Status

Initial application implementation. **End-to-end tests and browser validation are still pending.**

## Features

- OpenStreetMap basemap and fictional network overlay in an OpenLayers frontend
- Select a point by clicking the map
- Calculate and display the nearest network connection and its LineString
- Save studies in SQLite, keyed by fictional network and study code
- List and restore saved studies, including after restarting FastAPI
- Synthetic local GeoPackage generator and automated tests

## Run (Ubuntu/WSL2, conda-forge GDAL installed)

```bash
conda env create -f environment.yml
conda activate campinas-energy-app
python make_demo_data.py
python -m pytest -v
python verify_restart.py
bash run.sh
```

Open http://127.0.0.1:8000/app/

The generator refuses to overwrite existing GeoPackages. Run it only once unless you deliberately rename the existing demo file.

## Structure

- `backend/`: FastAPI, GIS repository and spatial/study services adapted from the validated V7 foundation
- `frontend/`: interactive OpenLayers application
- `make_demo_data.py`: fictional demo network
- `tests/`: backend and application tests
- `verify_restart.py`: verifies an HTTP study can be restored after a real server restart
- `VALIDATION_STATUS.md`: evidence and outstanding checks

**Data policy:** This repository is intended for synthetic demonstrations. No company repository, operational feeder dataset, real network identifier or production database is included. GIS results are illustrative, not electrical engineering approval.
