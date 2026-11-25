"""Static checks for the independent V7-based frontend."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend"

def test_frontend_calls_expected_backend_routes():
    source = (ROOT / "app.js").read_text(encoding="utf-8")
    for token in (
        '"/alimentadores"',
        '"/ssdmt"',
        '"/connection"',
        '"/studies/"',
        '"/studies"',
        'selected_point',
        'connection_point',
        'connection_line',
        "EPSG:4326",
        "EPSG:3857",
        'new ol.layer.Tile',
        "openstreetmap.org/copyright",
    ):
        assert token in source, f"Missing frontend contract: {token}"

def test_no_real_feeder_identifiers_in_app_frontend():
    text = "\n".join(p.read_text(encoding="utf-8") for p in ROOT.glob("*") if p.is_file())
    assert "AND11" not in text
    assert "CAMPINAS 5 - ANDORINHA" not in text
    assert "TESTE-V7-001" not in text
