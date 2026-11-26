"""Import one publicly obtained ANEEL BDGD snapshot into a local historical GeoPackage.

Requirements: GDAL/OGR Python bindings, ogr2ogr executable, and an official IBGE
municipal boundary polygon as GeoJSON/GPKG/Shapefile. No dataset is downloaded
automatically and no imported geometries are committed to Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from osgeo import ogr

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "backend" / "data" / "campinas_bdgd_historical.gpkg"


def validate_source(path: Path, layer_name: str) -> tuple[str, int]:
    ds = ogr.Open(str(path), 0)
    if ds is None:
        raise ValueError(f"Cannot open BDGD geodatabase: {path}")
    matching = next((ds.GetLayerByIndex(i) for i in range(ds.GetLayerCount())
                     if ds.GetLayerByIndex(i).GetName().casefold() == layer_name.casefold()), None)
    if matching is None:
        names = [ds.GetLayerByIndex(i).GetName() for i in range(ds.GetLayerCount())]
        raise ValueError(f"Layer {layer_name!r} not found. Available: {names}")
    name, count = matching.GetName(), matching.GetFeatureCount()
    ds = None
    return name, count


def validate_boundary(path: Path) -> None:
    ds = ogr.Open(str(path), 0)
    if ds is None or ds.GetLayerCount() == 0:
        raise ValueError(f"Cannot open municipal boundary: {path}")
    layer = ds.GetLayerByIndex(0)
    if layer.GetFeatureCount() != 1:
        raise ValueError("Boundary must contain exactly one Campinas municipality polygon")
    feature = layer.GetNextFeature()
    geom = feature.GetGeometryRef() if feature is not None else None
    if geom is None or geom.IsEmpty() or geom.GetGeometryType() not in (
        ogr.wkbPolygon, ogr.wkbMultiPolygon, ogr.wkbPolygon25D, ogr.wkbMultiPolygon25D
    ):
        raise ValueError("Boundary must contain a nonempty polygon or multipolygon")
    # Reject a polygon identified as another municipality.
    known_codes = ("CD_MUN", "CD_GEOCMU", "cd_geocmu", "codigo_ibge", "ibge_code")
    for name in known_codes:
        if feature.GetFieldIndex(name) >= 0:
            code = str(feature.GetField(name))
            if code != "3509502":
                raise ValueError(f"Boundary is not Campinas (IBGE 3509502): {code}")
            break
    else:
        raise ValueError("Boundary must contain an IBGE municipality-code field (e.g. CD_MUN=3509502)")
    spatial_ref = layer.GetSpatialRef()
    if spatial_ref is None:
        raise ValueError("Boundary layer must have a coordinate reference system")
    ds = None


def import_layer(source: Path, boundary: Path, output: Path, year: int,
                 source_url: str, layer: str = "SSDMT") -> dict:
    if not 2000 <= year <= datetime.now(timezone.utc).year:
        raise ValueError("Reference year is not plausible")
    if not source.exists() or not boundary.exists():
        raise FileNotFoundError("Source GDB and municipal boundary must both exist")
    if source.resolve() == output.resolve() or boundary.resolve() == output.resolve():
        raise ValueError("Output must not overwrite inputs")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing historical dataset: {output}")
    if shutil.which("ogr2ogr") is None:
        raise RuntimeError("ogr2ogr is unavailable; activate a GDAL-enabled Conda environment")
    source_name, source_count = validate_source(source, layer)
    validate_boundary(boundary)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.stem + ".partial.gpkg")
    if temp.exists():
        raise FileExistsError(f"Temporary file already exists: {temp}")
    cmd = [
        "ogr2ogr", "-f", "GPKG", str(temp), str(source), source_name,
        "-clipsrc", str(boundary),
        "-t_srs", "EPSG:4326",
        "-nln", "historical_ssdmt",
        "-lco", "SPATIAL_INDEX=YES",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        ds = ogr.Open(str(temp), 0)
        if ds is None:
            raise RuntimeError("Output GeoPackage cannot be reopened")
        result_layer = ds.GetLayerByName("historical_ssdmt")
        if result_layer is None:
            raise RuntimeError("Export did not produce expected layer")
        selected_count = result_layer.GetFeatureCount()
        ds = None
        if selected_count <= 0:
            raise ValueError("No features intersect the supplied municipal boundary")
        temp.rename(output)
    finally:
        if temp.exists():
            temp.unlink()

    sha256 = hashlib.sha256()
    with output.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha256.update(block)

    metadata = {
        "dataset": "Campinas BDGD historical public snapshot",
        "dataset_type": "historic_public_bdgd",
        "source_agency": "ANEEL",
        "distributor": "CPFL Paulista (verify file identity before import)",
        "source_url": source_url,
        "source_local_path": str(source.resolve()),
        "municipality": "Campinas",
        "ibge_code": "3509502",
        "municipal_boundary_path": str(boundary.resolve()),
        "reference_date": f"{year}-12-31",
        "source_layer": source_name,
        "target_layer": "historical_ssdmt",
        "source_total_features": source_count,
        "clipped_features": selected_count,
        "target_crs": "EPSG:4326",
        "output_sha256": sha256.hexdigest(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "Historical regulatory geospatial approximation, not live network status",
        "license_review": "Verify license conditions of the exact downloaded GDB before redistribution",
    }
    sidecar = output.with_suffix(".metadata.json")
    sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Unzipped public ANEEL BDGD .gdb path")
    parser.add_argument("--boundary", required=True, type=Path, help="IBGE Campinas polygon GeoJSON/GPKG")
    parser.add_argument("--year", required=True, type=int, help="Source snapshot reference year")
    parser.add_argument("--source-url", required=True, help="Source catalog/official download URL")
    parser.add_argument("--layer", default="SSDMT", help="Network layer (default SSDMT)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    info = import_layer(args.source, args.boundary, args.output, args.year,
                        args.source_url, args.layer)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
