from fastapi import APIRouter,Depends,HTTPException
from app.config import get_gpkg_path
from app.repositories.gpkg_repository import GeoPackageRepository
from app.services.feeder_service import FeederService
router=APIRouter(prefix="/alimentadores",tags=["alimentadores"])
def get_service():return FeederService(GeoPackageRepository(get_gpkg_path()))
@router.get("")
def list_feeders(service=Depends(get_service)):return {"alimentadores":service.list_feeders()}
@router.get("/{ctmt}")
def summary(ctmt,service=Depends(get_service)):
 r=service.get_summary(ctmt)
 if r is None:raise HTTPException(404,f"Alimentador {ctmt.upper()} not found")
 return r
@router.get("/{ctmt}/ssdmt")
def ssdmt(ctmt,service=Depends(get_service)):
 r=service.get_ssdmt(ctmt)
 if r is None:raise HTTPException(404,f"Alimentador {ctmt.upper()} not found")
 return r
@router.get("/{ctmt}/sub")
def sub(ctmt,service=Depends(get_service)):
 r=service.get_sub(ctmt)
 if r is None:raise HTTPException(404,f"Substation for {ctmt.upper()} not found")
 return r
@router.get("/{ctmt}/geojson")
def bundle(ctmt,service=Depends(get_service)):
 r=service.get_geojson_bundle(ctmt)
 if r is None:raise HTTPException(404,f"Alimentador {ctmt.upper()} not found")
 return r
