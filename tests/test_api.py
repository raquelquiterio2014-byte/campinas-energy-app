import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.alimentadores import get_service

class Fake:
    def list_feeders(self): return [{"ctmt":"TEST01","sub":"SUB","segment_count":2}]
    def get_summary(self,c): return None if c.upper()!="TEST01" else {"ctmt":"TEST01","segment_count":2,"phases":["ABC"],"substation":{"codigo":"SUB","nome":"Synthetic"}}
    def get_ssdmt(self,c): return None if c.upper()!="TEST01" else {"type":"FeatureCollection","features":[]}
    def get_sub(self,c): return None if c.upper()!="TEST01" else {"type":"FeatureCollection","features":[]}
    def get_geojson_bundle(self,c): return None if c.upper()!="TEST01" else {"alimentador":"TEST01","crs":"EPSG:4326","subestacao":{},"faseamentos":["ABC"],"ssdmt":self.get_ssdmt(c),"sub":self.get_sub(c)}

client = TestClient(app)

@pytest.fixture(autouse=True)
def fake_feeder_service():
    app.dependency_overrides[get_service] = lambda: Fake()
    yield
    app.dependency_overrides.pop(get_service, None)

def test_root():
    data = client.get("/").json()
    assert data["version"] == "app-0.1"
    assert data["map"] == "/map"

def test_list(): assert client.get("/alimentadores").status_code == 200
def test_summary(): assert client.get("/alimentadores/TEST01").json()["phases"] == ["ABC"]
def test_ssdmt(): assert client.get("/alimentadores/TEST01/ssdmt").json()["type"] == "FeatureCollection"
def test_sub(): assert client.get("/alimentadores/TEST01/sub").json()["type"] == "FeatureCollection"
def test_bundle(): assert client.get("/alimentadores/TEST01/geojson").json()["crs"] == "EPSG:4326"
def test_unknown(): assert client.get("/alimentadores/UNKNOWN").status_code == 404
