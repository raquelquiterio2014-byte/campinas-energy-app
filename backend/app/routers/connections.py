from fastapi import APIRouter,Depends,HTTPException
from app.config import get_gpkg_path
from app.repositories.gpkg_repository import GeoPackageRepository
from app.schemas.connection import ConnectionRequest
from app.services.spatial_connection_service import SpatialConnectionService
router=APIRouter(prefix="/alimentadores",tags=["spatial-connection"])
def get_connection_service():return SpatialConnectionService(GeoPackageRepository(get_gpkg_path()))
@router.post("/{ctmt}/connection")
def connection(ctmt:str,payload:ConnectionRequest,service=Depends(get_connection_service)):
 r=service.connect(ctmt,payload.longitude,payload.latitude)
 if r is None:raise HTTPException(404,f"Alimentador {ctmt.upper()} or usable geometry not found")
 return r
