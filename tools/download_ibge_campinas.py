"""Download IBGE SP municipalities 2024 and extract the exact Campinas polygon.

Uses only Python standard library and ogr2ogr installed in the project Conda
environment. Does not access any private electrical network data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from osgeo import ogr

SOURCE = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/"
          "malhas_territoriais/malhas_municipais/municipio_2024/UFs/SP/"
          "SP_Municipios_2024.zip")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "backend" / "data" / "campinas_ibge_boundary.gpkg"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    out = args.output.expanduser().resolve()
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite existing boundary: {out}")
    if shutil.which("ogr2ogr") is None:
        raise RuntimeError("ogr2ogr not installed (activate GDAL Conda environment)")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ibge-campinas-") as tmp:
        path = Path(tmp) / "SP_Municipios_2024.zip"
        with urllib.request.urlopen(SOURCE, timeout=120) as response, path.open("wb") as fd:
            shutil.copyfileobj(response, fd)
        archive_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        with zipfile.ZipFile(path) as archive:
            # Only accept normal data files without absolute paths or traversal
            for member in archive.namelist():
                dest = Path(member)
                if dest.is_absolute() or ".." in dest.parts:
                    raise ValueError(f"Unsafe ZIP path: {member}")
            archive.extractall(tmp)
        shp = list(Path(tmp).rglob("*.shp"))
        if len(shp) != 1:
            raise ValueError(f"Expected one municipal shapefile; found {shp}")
        source = ogr.Open(str(shp[0]), 0)
        if source is None: raise ValueError("IBGE Shapefile cannot be opened")
        layer = source.GetLayerByIndex(0)
        fields = [f.name for f in layer.schema]
        if "CD_MUN" not in fields:
            raise ValueError(f"IBGE shapefile CD_MUN field missing. Fields: {fields}")
        source = None
        cmd = ["ogr2ogr", "-f", "GPKG", str(out), str(shp[0]),
               "-where", "CD_MUN = '3509502'", "-nln", "municipio"]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            ds = ogr.Open(str(out))
            lay = ds.GetLayerByName("municipio") if ds is not None else None
            if lay is None or lay.GetFeatureCount() != 1:
                raise ValueError("IBGE extraction must produce exactly one Campinas polygon")
            feat = lay.GetNextFeature()
            assert str(feat.GetField("CD_MUN")) == "3509502"
            ds = None
        except Exception:
            if out.exists(): out.unlink()
            raise
    info = {
        "municipality": "Campinas", "ibge_code": "3509502",
        "source": SOURCE, "reference_year": 2024,
        "source_archive_sha256": archive_hash, "boundary": str(out)
    }
    out.with_suffix(".source.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
