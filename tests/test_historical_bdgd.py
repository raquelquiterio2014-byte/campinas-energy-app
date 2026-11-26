"""Small synthetic integration test for the historical BDGD clipping import."""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from osgeo import ogr, osr

from tools.import_bdgd_campinas import import_layer


def _srs():
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(4326)
    return crs


def _line(ds, code, coords):
    layer = ds.GetLayerByName("SSDMT")
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField("cod_id", code)
    feature.SetField("ctmt", "SYN-HISTORY")
    line = ogr.Geometry(ogr.wkbLineString)
    for lon, lat in coords:
        line.AddPoint_2D(lon, lat)
    feature.SetGeometry(line)
    layer.CreateFeature(feature)


def _make_source(path):
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(str(path))
    layer = ds.CreateLayer("SSDMT", _srs(), ogr.wkbLineString)
    for col in ("cod_id", "ctmt"):
        layer.CreateField(ogr.FieldDefn(col, ogr.OFTString))
    _line(ds, "INSIDE", [(-47.05, -22.91), (-47.04, -22.90)])
    _line(ds, "OUTSIDE", [(-48.10, -23.50), (-48.00, -23.40)])
    ds = None


def _make_boundary(path, code="3509502"):
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(str(path))
    layer = ds.CreateLayer("municipio", _srs(), ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn("CD_MUN", ogr.OFTString))
    feat = ogr.Feature(layer.GetLayerDefn())
    feat.SetField("CD_MUN", code)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x, y in [(-47.10, -22.95), (-47.0, -22.95),
                 (-47.0, -22.85), (-47.10, -22.85), (-47.10, -22.95)]:
        ring.AddPoint_2D(x, y)
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    feat.SetGeometry(polygon)
    layer.CreateFeature(feat)
    ds = None


def test_historical_import_clips_and_writes_provenance():
    with TemporaryDirectory() as folder:
        tmp = Path(folder)
        source = tmp / "source.gpkg"
        boundary = tmp / "boundary.gpkg"
        output = tmp / "history.gpkg"
        _make_source(source)
        _make_boundary(boundary)
        metadata = import_layer(source, boundary, output, 2022, "https://example.invalid/official-catalog")
        assert metadata["reference_date"] == "2022-12-31"
        assert metadata["source_total_features"] == 2
        assert metadata["clipped_features"] == 1
        assert len(metadata["output_sha256"]) == 64
        assert output.with_suffix(".metadata.json").exists()
        ds = ogr.Open(str(output))
        layer = ds.GetLayerByName("historical_ssdmt")
        assert layer.GetFeatureCount() == 1
        assert layer.GetNextFeature().GetField("cod_id") == "INSIDE"
        ds = None
        with pytest.raises(FileExistsError):
            import_layer(source, boundary, output, 2022, "https://example.invalid")


def test_historical_import_rejects_wrong_municipality():
    with TemporaryDirectory() as folder:
        tmp = Path(folder)
        source = tmp / "source.gpkg"
        boundary = tmp / "boundary.gpkg"
        _make_source(source)
        _make_boundary(boundary, "3550308")
        with pytest.raises(ValueError, match="not Campinas"):
            import_layer(source, boundary, tmp / "out.gpkg", 2022, "https://example.invalid")
