# Campinas Energy App — Historical public network layer

## Objective

Prepare a **local, historically dated** municipal cutout from the ANEEL BDGD
CPFL Paulista public distribution-network dataset. This work is independent
of the ERA Energy residency code and is **not** a live operational network.

## Source inventory (research on 2026-11-25)

1. **ANEEL BDGD catalog**:
   https://dadosabertos.aneel.gov.br/dataset/base-de-dados-geografica-da-distribuidora-bdgd
   - Official SIG-R regulatory geodatabase. Cartographic files are organized
     by distributor as File Geodatabases (`.gdb`); source catalog lists ODbL.
   - Portal updates annually. The catalog's update timestamp does **not**
     automatically identify the reference date of a particular GDB.
2. **CPFL Paulista item found, reference 2022-12-31**:
   https://hub.arcgis.com/datasets/7990de7f137e4e49857b48f18e633558
   - Label: `CPFL Paulista 63 2022-12-31 V11 20231103-1308`
   - File Geodatabase, listed as publicly viewable.
   - The item itself displayed **No License Provided**. Confirm terms for the
     particular download; do not assume unrestricted redistribution.
   - A more recent **specific CPFL Paulista GDB download has not been
     verified** in this initial research.
3. **IBGE official municipal boundaries**:
   https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
   - Campinas municipality code: `3509502`.
   - Select the matching municipal polygon from the official SP shapefile;
     use its code field `CD_MUN`.

## Obtain the source files manually

Download the particular BDGD GDB through the ANEEL catalog/ArcGIS Hub, noting
the source URL, actual snapshot reference date, and terms of use. Extract the
downloaded ZIP locally. The import script accepts an **unpacked GDB directory**.

Download the official IBGE São Paulo municipal boundary shapefile and extract
it. You can inspect the source using GDAL, without QGIS:

```bash
ogrinfo -so -al "/path/to/CPFL_PAULISTA.gdb"
ogrinfo -so -al "/path/to/SP_Municipios.shp"
```

Create a **single-feature** Campinas boundary layer, retaining `CD_MUN`:

```bash
mkdir -p backend/data
ogr2ogr -f GPKG backend/data/campinas_ibge_boundary.gpkg \
  "/path/to/SP_Municipios.shp" \
  -where "CD_MUN = '3509502'" -nln municipio
```

If the official IBGE layer has different field names, inspect its schema
first and adapt the where-clause accordingly. Verify it contains exactly
**one** polygon with `CD_MUN=3509502`.

## Build the local historical snapshot

Run from the repository root, after activating the geospatial conda env:

```bash
python tools/import_bdgd_campinas.py \
  --source "/path/to/CPFL_PAULISTA.gdb" \
  --boundary backend/data/campinas_ibge_boundary.gpkg \
  --year 2022 \
  --source-url "https://hub.arcgis.com/datasets/7990de7f137e4e49857b48f18e633558"
```

**The `--year` must reflect the actual GDB snapshot**, not the download year.
Use `--year 2022` only with the confirmed 2022 source or update it for a
different source.

Outputs (not tracked by Git):

- `backend/data/campinas_bdgd_historical.gpkg` containing
  `historical_ssdmt` in `EPSG:4326`;
- `backend/data/campinas_bdgd_historical.metadata.json` with reference date,
  source URL/path, selected feature count and SHA-256 checksum.

Inspect the resulting layer:

```bash
ogrinfo -so backend/data/campinas_bdgd_historical.gpkg historical_ssdmt
python -m pytest -v tests/test_historical_bdgd.py
```

## Status and constraints

- [x] Source catalog, 2022 CPFL Paulista record, and official municipality source identified
- [x] Local import + polygon clipping script implemented
- [x] Provenance and output checksum recorded by the importer
- [x] Data-file exclusion from public Git configured
- [x] Synthetic import tests authored
- [ ] Confirm direct official GDB download and its license
- [ ] Download actual source GDB and official boundary to local WSL
- [ ] Execute the import on the real public historical GDB
- [ ] Verify feature counts, spatial reference, geometry quality and SHA-256
- [ ] Add separately identified **Historical BDGD** map layer to the app UI
- [ ] Run automated/browser tests and document evidence

This importer does **not** alter `demo-network.gpkg` or
`demo-studies.db`. No imported BDGD geometry should be committed to this
public repository until a specific source's reuse license has been
verified.

A point-to-network geometric distance on historical BDGD is **not**
proof of power availability, technical feasibility, approval of electrical
connection, or current real-world topology.
