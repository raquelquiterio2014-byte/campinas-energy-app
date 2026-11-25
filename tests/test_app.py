"""App-level smoke and synthetic end-to-end tests (run in era-gis)."""
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app_server import app
from make_demo_data import create

client = TestClient(app)

def test_frontend_resources_and_backend_docs():
    assert client.get("/app/").status_code == 200
    html = client.get("/app/").text
    assert 'id="map"' in html
    assert 'id="save"' in html
    assert 'id="restore"' in html
    assert client.get("/app/app.js").status_code == 200
    assert client.get("/app/styles.css").status_code == 200
    assert client.get("/docs").status_code == 200

def test_synthetic_study_lifecycle(monkeypatch):
    with TemporaryDirectory() as tmp:
        gpkg = Path(tmp) / "synthetic.gpkg"
        db = Path(tmp) / "studies.db"
        create(gpkg)
        monkeypatch.setenv("ERA_GPKG_PATH", str(gpkg))
        monkeypatch.setenv("ERA_STUDIES_DB_PATH", str(db))
        feeders = client.get("/alimentadores")
        assert feeders.status_code == 200
        assert {f["ctmt"] for f in feeders.json()["alimentadores"]} == {"SYN-A", "SYN-B"}
        geom = client.get("/alimentadores/SYN-A/ssdmt")
        assert geom.status_code == 200
        assert len(geom.json()["features"]) == 2
        payload = {"longitude": -47.052, "latitude": -22.913}
        calculated = client.post("/alimentadores/SYN-A/connection", json=payload)
        assert calculated.status_code == 200
        assert calculated.json()["connection_line"]["type"] == "LineString"
        saved = client.post("/alimentadores/SYN-A/studies/APP-DEMO-001", json=payload)
        assert saved.status_code == 201
        stored = saved.json()
        assert stored["selected_point"]["coordinates"] == [payload["longitude"], payload["latitude"]]
        assert client.post("/alimentadores/SYN-A/studies/APP-DEMO-001", json=payload).status_code == 409
        assert client.get("/alimentadores/SYN-A/studies/MISSING").status_code == 404
        assert client.get("/alimentadores/SYN-A/studies").json()[0]["study_code"] == "APP-DEMO-001"
        restored = client.get("/alimentadores/SYN-A/studies/APP-DEMO-001")
        assert restored.status_code == 200
        assert restored.json()["connection_line"] == stored["connection_line"]
        assert restored.json()["selected_point"] == stored["selected_point"]
