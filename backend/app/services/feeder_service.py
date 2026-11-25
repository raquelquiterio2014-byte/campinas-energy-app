class FeederService:
 def __init__(self,repository):self.repository=repository
 def list_feeders(self):return self.repository.list_feeders()
 def get_summary(self,ctmt):return self.repository.feeder_summary(ctmt.upper())
 def get_ssdmt(self,ctmt):return self.repository.ssdmt_geojson(ctmt.upper())
 def get_sub(self,ctmt):return self.repository.sub_geojson_for_feeder(ctmt.upper())
 def get_geojson_bundle(self,ctmt):
  n=ctmt.upper();s=self.repository.feeder_summary(n)
  if s is None:return None
  return {"alimentador":n,"crs":"EPSG:4326","subestacao":s["substation"],"faseamentos":s["phases"],"ssdmt":self.repository.ssdmt_geojson(n),"sub":self.repository.sub_geojson_for_feeder(n)}
