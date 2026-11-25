from fastapi import APIRouter, Depends, HTTPException
from app.config import get_gpkg_path, get_studies_db_path
from app.repositories.gpkg_repository import GeoPackageRepository
from app.repositories.study_repository import StudyRepository, DuplicateStudyError
from app.schemas.connection import ConnectionRequest
from app.services.spatial_connection_service import SpatialConnectionService
from app.services.study_service import StudyService

router = APIRouter(prefix="/alimentadores", tags=["studies"])

def get_study_service():
    network_repo = GeoPackageRepository(get_gpkg_path())
    study_repo = StudyRepository(get_studies_db_path())
    return StudyService(study_repo, SpatialConnectionService(network_repo))

@router.post("/{ctmt}/studies/{study_code}", status_code=201)
def save_study(ctmt: str, study_code: str, payload: ConnectionRequest, service=Depends(get_study_service)):
    code = study_code.strip()
    if not code:
        raise HTTPException(422, "Study code cannot be empty")
    try:
        result = service.calculate_and_save(ctmt.upper(), code, payload.longitude, payload.latitude)
    except DuplicateStudyError:
        raise HTTPException(409, f"Study {code} already exists for feeder {ctmt.upper()}")
    if result is None:
        raise HTTPException(404, f"Alimentador {ctmt.upper()} or usable geometry not found")
    return result

@router.get("/{ctmt}/studies")
def list_studies(ctmt: str, service=Depends(get_study_service)):
    return service.list_for_feeder(ctmt.upper())

@router.get("/{ctmt}/studies/{study_code}")
def restore_study(ctmt: str, study_code: str, service=Depends(get_study_service)):
    result = service.restore(ctmt.upper(), study_code)
    if result is None:
        raise HTTPException(404, f"Study {study_code} not found for feeder {ctmt.upper()}")
    return result
