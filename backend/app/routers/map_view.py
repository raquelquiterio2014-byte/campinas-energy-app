from html import escape
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.config import get_osm_tile_url

router = APIRouter(tags=["map"])

@router.get("/map", response_class=HTMLResponse)
def map_view():
    tile_url = escape(get_osm_tile_url(), quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Campinas Energy App — Map</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ol@10.6.1/ol.css">
<script src="https://cdn.jsdelivr.net/npm/ol@10.6.1/dist/ol.js"></script>
<style>
html,body,#map{{margin:0;width:100%;height:100%;font-family:Arial,sans-serif}}
.panel{{position:absolute;z-index:10;top:12px;left:12px;background:#fff;padding:12px;border-radius:8px;
box-shadow:0 2px 10px #0003;max-width:360px}}
.panel h1{{font-size:16px;margin:0 0 6px}} .panel p{{font-size:12px;margin:0;color:#444}}
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
<h1>Campinas Energy App</h1>
<p>OpenStreetMap basemap served through the backend map route. Network data remains available through the GeoJSON API.</p>
</div>
<script>
const raster = new ol.layer.Tile({{
  source: new ol.source.XYZ({{
    url: "{tile_url}",
    attributions: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }})
}});
const map = new ol.Map({{
  target: "map",
  layers: [raster],
  view: new ol.View({{center: ol.proj.fromLonLat([-47.06,-22.91]), zoom: 11}})
}});
</script>
</body>
</html>"""
