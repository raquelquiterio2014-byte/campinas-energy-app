from __future__ import annotations
import json
from pathlib import Path
from osgeo import ogr
ogr.UseExceptions()
class GeoPackageRepository:
    def __init__(self,gpkg_path:Path)->None:self.gpkg_path=gpkg_path
    def _open(self):
        if not self.gpkg_path.exists():raise FileNotFoundError(f"GeoPackage not found: {self.gpkg_path}")
        ds=ogr.Open(str(self.gpkg_path),0)
        if ds is None:raise RuntimeError(f"Unable to open GeoPackage: {self.gpkg_path}")
        return ds
    @staticmethod
    def _feature_to_geojson(f):return json.loads(f.ExportToJson())
    def list_feeders(self):
        ds=self._open();r=ds.ExecuteSQL("SELECT ctmt, sub, COUNT(*) AS segment_count FROM ssdmt WHERE ctmt IS NOT NULL GROUP BY ctmt, sub ORDER BY ctmt")
        try:return [{"ctmt":f.GetField("ctmt"),"sub":f.GetField("sub"),"segment_count":f.GetField("segment_count")} for f in r]
        finally:ds.ReleaseResultSet(r)
    def _phases(self,ds,ctmt):
        r=ds.ExecuteSQL(f"SELECT DISTINCT fas_con FROM ssdmt WHERE ctmt = '{ctmt}' AND fas_con IS NOT NULL ORDER BY fas_con")
        try:return [f.GetField("fas_con") for f in r]
        finally:ds.ReleaseResultSet(r)
    def _substation(self,ds,code):
        if not code:return None
        safe=code.replace("'","''");r=ds.ExecuteSQL(f"SELECT cod_id, nome FROM sub WHERE cod_id = '{safe}'")
        try:
            f=r.GetNextFeature();return {"codigo":code,"nome":None} if f is None else {"codigo":f.GetField("cod_id"),"nome":f.GetField("nome")}
        finally:ds.ReleaseResultSet(r)
    def feeder_summary(self,ctmt):
        ds=self._open();safe=ctmt.replace("'","''");r=ds.ExecuteSQL(f"SELECT ctmt, sub, COUNT(*) AS segment_count FROM ssdmt WHERE ctmt = '{safe}' GROUP BY ctmt, sub")
        try:
            f=r.GetNextFeature()
            if f is None:return None
            return {"ctmt":f.GetField("ctmt"),"segment_count":f.GetField("segment_count"),"phases":self._phases(ds,safe),"substation":self._substation(ds,f.GetField("sub"))}
        finally:ds.ReleaseResultSet(r)
    def ssdmt_geojson(self,ctmt):
        ds=self._open();layer=ds.GetLayerByName("ssdmt");safe=ctmt.replace("'","''");layer.SetAttributeFilter(f"ctmt = '{safe}'");features=[self._feature_to_geojson(f) for f in layer];return None if not features else {"type":"FeatureCollection","features":features}
    def sub_geojson_for_feeder(self,ctmt):
        summary=self.feeder_summary(ctmt)
        if summary is None or summary["substation"] is None:return None
        ds=self._open();layer=ds.GetLayerByName("sub");code=summary["substation"]["codigo"].replace("'","''");layer.SetAttributeFilter(f"cod_id = '{code}'");return {"type":"FeatureCollection","features":[self._feature_to_geojson(f) for f in layer]}
    def feeder_segments(self,ctmt):
        ds=self._open();layer=ds.GetLayerByName("ssdmt");safe=ctmt.replace("'","''");layer.SetAttributeFilter(f"ctmt = '{safe}'");out=[]
        for f in layer:
            g=f.GetGeometryRef()
            if g is None or g.IsEmpty():continue
            out.append({"cod_id":f.GetField("cod_id"),"ctmt":f.GetField("ctmt"),"fas_con":f.GetField("fas_con"),"geometry_wkb":bytes(g.ExportToWkb())})
        return out
