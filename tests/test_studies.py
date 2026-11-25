from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from osgeo import ogr
from app.repositories.study_repository import StudyRepository, DuplicateStudyError
from app.services.spatial_connection_service import SpatialConnectionService
from app.services.study_service import StudyService

class NetworkRepo:
    def feeder_segments(self, feeder):
        if feeder != "TEST01":
            return []
        g = ogr.Geometry(ogr.wkbLineString)
        g.AddPoint_2D(-47.0, -22.9)
        g.AddPoint_2D(-46.99, -22.9)
        return [{"cod_id":"SEG-1","ctmt":"TEST01","fas_con":"ABC","geometry_wkb":bytes(g.ExportToWkb())}]

def make_service(path):
    return StudyService(StudyRepository(path), SpatialConnectionService(NetworkRepo()))

def test_save_and_restore_persists_after_repository_reopen():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "studies.db"
        first = make_service(db)
        saved = first.calculate_and_save("TEST01", "STU-001", -46.995, -22.895)
        assert saved["study_code"] == "STU-001"
        assert saved["connection_line"]["type"] == "LineString"
        second = make_service(db)
        restored = second.restore("TEST01", "STU-001")
        assert restored["selected_point"] == saved["selected_point"]
        assert restored["connection_line"] == saved["connection_line"]

def test_duplicate_study_is_rejected():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "studies.db"
        service = make_service(db)
        service.calculate_and_save("TEST01", "STU-001", -46.995, -22.895)
        with pytest.raises(DuplicateStudyError):
            service.calculate_and_save("TEST01", "STU-001", -46.995, -22.895)

def test_list_studies_by_feeder():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "studies.db"
        service = make_service(db)
        service.calculate_and_save("TEST01", "A", -46.995, -22.895)
        service.calculate_and_save("TEST01", "B", -46.994, -22.894)
        assert [x["study_code"] for x in service.list_for_feeder("TEST01")] == ["A", "B"]

def test_unknown_feeder_is_not_saved():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "studies.db"
        service = make_service(db)
        assert service.calculate_and_save("UNKNOWN", "X", -46.995, -22.895) is None
        assert service.restore("UNKNOWN", "X") is None
