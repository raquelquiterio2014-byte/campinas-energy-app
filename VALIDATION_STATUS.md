# Campinas Energy App — Validation status

## Project separation

This is an independent **Campinas Energy App** repository, based on the V7 GIS backend architecture. It is not ERA Energy V8 and does not contain the company's repository or production data.

## Implementation checklist

- [x] Public repository initialized with application code (synthetic-demo only)
- [x] Frontend map, fictional network overlay, click selection and connection display implemented
- [x] FastAPI API and SQLite save/restore code integrated
- [x] Synthetic local GeoPackage generator included
- [x] Pytest regression and application tests included
- [x] Script for actual server restart and geometry restoration included
- [x] CI workflow configured
- [ ] CI runs confirmed green
- [x] Browser OSM tiles visually verified (user-provided screenshot)
- [x] Selected point and calculated line visually verified (user-provided screenshot)
- [x] Study save/restore confirmed in browser (user-provided screenshots)
- [x] Manual save, requested server restart, and subsequent retrieval reported by user; screenshot confirms retrieved study after that procedure
- [ ] Screenshot image files and automated test logs committed to repository

All unchecked items are pending verification; do not confuse implementation with a passing validation.

## Commands

```bash
git clone https://github.com/raquelquiterio2014-byte/campinas-energy-app.git
cd campinas-energy-app
conda env create -f environment.yml
conda activate campinas-energy-app
python make_demo_data.py
python -m pytest -v
python verify_restart.py
bash run.sh
```

Visit http://127.0.0.1:8000/app/ and follow the map interaction workflow.

## Expected manual flow

Choose a fictional feeder (SYN-A), click the map, calculate the line, type code DEMO-APP-001, save, stop Uvicorn, restart with `bash run.sh`, and restore using the same feeder and code. Verify that point and line geometries match the originally saved study.

No live electrical network data is included.

## Manual browser evidence — 2026-11-25 (Brazil local date)

The user demonstrated the application in a local browser at `127.0.0.1:8000/app/` and supplied screenshots showing:

1. FastAPI indicator **API online**, OpenStreetMap tiles rendered, and fictional feeder `SYN-A` with **2 segments** visible.
2. Selected location on the map and calculated spatial connection: **phase ABC**, **0.204 km** displayed, status **Calculated**, with network/selected point/connection point/connection line visible.
3. Study code `CAMP-TEST-001` saved: UI displayed `Study CAMP-TEST-001 saved in SQLite (ID 1).` and status **Saved**.
4. Following the prior stop/restart instruction, restored study `CAMP-TEST-001`: UI displayed `Study CAMP-TEST-001 restored from SQLite, including the original point and connection line.` and status **Restored**, with **phase ABC**, **0.204 km** and geometry overlay visible.

These are **manual visual observations** based on user-provided screenshots. The screenshot image binaries are not committed to this repository. The screenshot alone does not independently document the terminal's shutdown/restart commands, compare exact geometry JSON, or establish automated test passing. The dedicated `verify_restart.py` and Pytest suite remain to be executed and their output recorded.
