from fastapi import FastAPI, HTTPException
from app.config import get_gpkg_path
from app.routers.alimentadores import router as alimentadores_router
from app.routers.connections import router as connections_router
from app.routers.studies import router as studies_router
from app.routers.map_view import router as map_router

app = FastAPI(
    title="Campinas Energy App API",
    description="Synthetic GIS study backend, map, and persistence.",
    version="app-0.1",
)

app.include_router(alimentadores_router)
app.include_router(connections_router)
app.include_router(studies_router)
app.include_router(map_router)

@app.get("/")
def root():
    return {
        "message": "Campinas Energy App API",
        "version": app.version,
        "map": "/map",
        "docs": "/docs",
    }

@app.get("/health", responses={503: {"description": "GeoPackage is not available"}})
def health():
    if not get_gpkg_path().exists():
        raise HTTPException(status_code=503, detail="GeoPackage is not available")
    return {"status": "ok", "gpkg_available": True}
