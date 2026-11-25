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
- [ ] Browser OSM tiles visually verified
- [ ] Selected point and calculated line visually verified
- [ ] Study save/restore confirmed in browser
- [ ] FastAPI stop/restart/retrieve confirmed in local WSL
- [ ] Final screenshot evidence and test log registered

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
