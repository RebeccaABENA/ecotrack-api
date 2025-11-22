from datetime import datetime,date
from typing import List, Optional
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File
from sqlalchemy.orm import Session

from .database import get_db
from . import schemas, crud
from .auth import get_current_user  # pour protéger les routes
from .models import User
from .importer import (
    import_indicators_from_csv,
    import_fr_e2_dataset,
    import_ind_atmo_dataset,
)


router = APIRouter(
    prefix="/api",
    tags=["data"],
)


@router.post("/zones", response_model=schemas.ZoneRead, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: schemas.ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # besoin d'être connecté
):
    return crud.create_zone(db, zone_in)


@router.get("/zones", response_model=List[schemas.ZoneRead])
def list_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_zones(db)


# ---------- SOURCES ---------- #

@router.post("/sources", response_model=schemas.SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(
    source_in: schemas.SourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_source(db, source_in)


@router.get("/sources", response_model=List[schemas.SourceRead])
def list_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_sources(db)


# ---------- INDICATORS ---------- #

@router.post("/indicators", response_model=schemas.IndicatorRead, status_code=status.HTTP_201_CREATED)
def create_indicator(
    indicator_in: schemas.IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # (optionnel) vérifier que la zone et la source existent
    if not crud.get_zone(db, indicator_in.zone_id):
        raise HTTPException(status_code=400, detail="Zone not found")
    if not crud.get_source(db, indicator_in.source_id):
        raise HTTPException(status_code=400, detail="Source not found")

    return crud.create_indicator(db, indicator_in)


@router.get("/indicators", response_model=List[schemas.IndicatorRead])
def list_indicators(
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_indicators(
        db=db,
        type=type,
        zone_id=zone_id,
        source_id=source_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
@router.get("/indicators/stats", response_model=schemas.IndicatorStats)
def get_indicator_stats(
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    GET /api/indicators/stats

    Retourne des stats agrégées sur les indicateurs :
    - count
    - min_value
    - max_value
    - avg_value

    avec les filtres optionnels :
    - type
    - zone_id
    - source_id
    - date_from, date_to (ISO 8601)
    """
    stats = crud.indicator_stats(
        db=db,
        type=type,
        zone_id=zone_id,
        source_id=source_id,
        date_from=date_from,
        date_to=date_to,
    )
    return stats
@router.post("/indicators/import_csv")
async def import_indicators_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un CSV.",
        )

    content = (await file.read()).decode("utf-8").splitlines()
    f = StringIO("\n".join(content))

    try:
        result = import_indicators_from_csv(db, f)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result

@router.post("/import/fr_e2")
async def import_fr_e2(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import spécifique du fichier FR_E2_2025-01-01.csv (ATMO GRAND EST).

    Le fichier doit être en séparateur ';' et contenir les colonnes
    décrites dans import_fr_e2_dataset.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")

    content = (await file.read()).decode("utf-8").splitlines()
    f = StringIO("\n".join(content))

    try:
        result = import_fr_e2_dataset(db, f)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result
@router.post("/import/ind_atmo")
async def import_ind_atmo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import spécifique du fichier ind_atmo_2021.csv (indices ATMO par commune).

    Séparateur ',' ; colonnes : lib_zone, source, date_ech, code_qual, lib_qual...
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")

    content = (await file.read()).decode("utf-8").splitlines()
    f = StringIO("\n".join(content))

    try:
        result = import_ind_atmo_dataset(db, f)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result

@router.put("/indicators/{indicator_id}", response_model=schemas.IndicatorRead)
def update_indicator(
    indicator_id: int,
    indicator_in: schemas.IndicatorCreate,  # ou un schema partial si tu en as un
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    indicator = crud.get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    updated = crud.update_indicator(db, indicator, indicator_in)
    return updated