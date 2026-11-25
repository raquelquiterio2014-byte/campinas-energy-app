from math import inf
from osgeo import ogr
from pyproj import Geod
from shapely import from_wkb
from shapely.geometry import Point
from shapely.ops import nearest_points
class SpatialConnectionService:
 def __init__(self,repository):self.repository=repository
 @staticmethod
 def _geodesic_length_km(a,b):
  _,_,m=Geod(ellps="WGS84").inv(a.GetX(),a.GetY(),b.GetX(),b.GetY());return m/1000.0
 def connect(self,ctmt,longitude,latitude):
  n=ctmt.upper();segments=self.repository.feeder_segments(n)
  if not segments:return None
  selected=ogr.Geometry(ogr.wkbPoint);selected.AddPoint_2D(longitude,latitude);sp=Point(longitude,latitude);best_d=inf;best=None;best_p=None
  for seg in segments:
   geom=from_wkb(seg["geometry_wkb"])
   if geom.is_empty:continue
   _,p=nearest_points(sp,geom);near=ogr.Geometry(ogr.wkbPoint);near.AddPoint_2D(p.x,p.y);d=self._geodesic_length_km(selected,near)
   if d<best_d:best_d,best,best_p=d,seg,near
  if best is None:return None
  a=[selected.GetX(),selected.GetY()];b=[best_p.GetX(),best_p.GetY()]
  return {"feeder":n,"phase":best.get("fas_con"),"network_element_id":best.get("cod_id"),"length_km":round(best_d,6),"selected_point":{"type":"Point","coordinates":a},"connection_point":{"type":"Point","coordinates":b},"connection_line":{"type":"LineString","coordinates":[a,b]},"crs":"EPSG:4326"}
