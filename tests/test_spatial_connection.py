from osgeo import ogr
from app.services.spatial_connection_service import SpatialConnectionService
class Repo:
 def feeder_segments(self,c):
  if c!="TEST01":return []
  g=ogr.Geometry(ogr.wkbLineString);g.AddPoint_2D(-47.0,-22.9);g.AddPoint_2D(-46.99,-22.9)
  return [{"cod_id":"SEG-1","ctmt":"TEST01","fas_con":"ABC","geometry_wkb":bytes(g.ExportToWkb())}]
def test_connection():
 r=SpatialConnectionService(Repo()).connect("test01",-46.995,-22.895);assert r["phase"]=="ABC" and r["length_km"]>0 and r["connection_line"]["type"]=="LineString"
def test_on_network():assert SpatialConnectionService(Repo()).connect("TEST01",-46.995,-22.9)["length_km"]<0.001
def test_unknown():assert SpatialConnectionService(Repo()).connect("UNKNOWN",-46.995,-22.895) is None
