from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_map_contains_osm_tiles_and_attribution():
    response = client.get("/map")
    assert response.status_code == 200
    assert "tile.openstreetmap.org" in response.text
    assert "OpenStreetMap contributors" in response.text
    assert "ol.Map" in response.text
