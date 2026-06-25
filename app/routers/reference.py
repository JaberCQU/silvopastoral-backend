# ============================================================
# Reference data routes -- GET /reference/species, GET /reference/regions
# ============================================================
# These are PUBLIC (no login required) and read-only. They exist
# to replace the hardcoded SPECIES and REGIONS JavaScript objects
# in the Phase 1 frontend's app.js, so that updating a sawmill
# distance or adding a new species no longer requires touching
# frontend code or redeploying GitHub Pages -- just an update to
# this database table.
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/species", response_model=List[schemas.SpeciesOut])
def list_species(db: Session = Depends(get_db)):
    return db.query(models.SpeciesReference).all()


@router.get("/regions", response_model=List[schemas.RegionOut])
def list_regions(db: Session = Depends(get_db)):
    return db.query(models.RegionReference).all()
