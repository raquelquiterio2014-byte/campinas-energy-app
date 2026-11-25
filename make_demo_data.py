"""Create a small fictional GeoPackage for local demonstrations. Never use operational data."""
from pathlib import Path
from osgeo import ogr, osr

OUTPUT = Path(__file__).resolve().parent / "backend" / "data" / "demo-network.gpkg"

def create(path=OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing data: {path}")
    driver = ogr.GetDriverByName("GPKG")
    ds = driver.CreateDataSource(str(path))
    if ds is None:
        raise RuntimeError("Could not create synthetic GeoPackage")
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(4326)
    network = ds.CreateLayer("ssdmt", crs, ogr.wkbLineString)
    for field in ("cod_id", "ctmt", "sub", "fas_con"):
        network.CreateField(ogr.FieldDefn(field, ogr.OFTString))
    sub = ds.CreateLayer("sub", crs, ogr.wkbPoint)
    for field in ("cod_id", "nome"):
        sub.CreateField(ogr.FieldDefn(field, ogr.OFTString))
    samples = [
        ("SYN-A01", "SYN-A", "SYN-01", [(-47.058, -22.910), (-47.048, -22.907), (-47.038, -22.903)]),
        ("SYN-A02", "SYN-A", "SYN-01", [(-47.048, -22.907), (-47.046, -22.897)]),
        ("SYN-B01", "SYN-B", "SYN-02", [(-47.078, -22.928), (-47.068, -22.923), (-47.058, -22.919)]),
    ]
    for code, feeder, station, coords in samples:
        feat = ogr.Feature(network.GetLayerDefn())
        for key, value in {"cod_id": code, "ctmt": feeder, "sub": station, "fas_con": "ABC"}.items():
            feat.SetField(key, value)
        geom = ogr.Geometry(ogr.wkbLineString)
        for lon, lat in coords:
            geom.AddPoint_2D(lon, lat)
        feat.SetGeometry(geom)
        network.CreateFeature(feat)
    for code, (lon, lat) in (("SYN-01", (-47.058, -22.910)), ("SYN-02", (-47.078, -22.928))):
        feat = ogr.Feature(sub.GetLayerDefn())
        feat.SetField("cod_id", code)
        feat.SetField("nome", "FICTIONAL DEMO SUBSTATION")
        geom = ogr.Geometry(ogr.wkbPoint)
        geom.AddPoint_2D(lon, lat)
        feat.SetGeometry(geom)
        sub.CreateFeature(feat)
    ds = None
    return path

if __name__ == "__main__":
    print(f"Created fictional GeoPackage: {create()}")
