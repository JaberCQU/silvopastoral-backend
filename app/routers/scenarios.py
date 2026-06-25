# ============================================================
# Scenario routes -- CRUD for saved dashboard input snapshots
# ============================================================
# A scenario belongs to a station, which belongs to a user, so
# every route here checks ownership through that chain before
# allowing access -- a user can only see/edit scenarios under
# their own stations.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth
from app.routers.stations import _get_owned_station_or_404

router = APIRouter(prefix="/stations/{station_id}/scenarios", tags=["scenarios"])


@router.post("", response_model=schemas.ScenarioOut, status_code=status.HTTP_201_CREATED)
def create_scenario(
    station_id: int,
    payload: schemas.ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_station_or_404(station_id, db, current_user)  # ownership check
    scenario = models.Scenario(**payload.model_dump(), station_id=station_id)
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.get("", response_model=List[schemas.ScenarioOut])
def list_scenarios(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_station_or_404(station_id, db, current_user)
    return db.query(models.Scenario).filter(models.Scenario.station_id == station_id).all()


@router.get("/{scenario_id}", response_model=schemas.ScenarioOut)
def get_scenario(
    station_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_station_or_404(station_id, db, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(models.Scenario.id == scenario_id, models.Scenario.station_id == station_id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.put("/{scenario_id}", response_model=schemas.ScenarioOut)
def update_scenario(
    station_id: int,
    scenario_id: int,
    payload: schemas.ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_station_or_404(station_id, db, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(models.Scenario.id == scenario_id, models.Scenario.station_id == station_id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    for field, value in payload.model_dump().items():
        setattr(scenario, field, value)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    station_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_station_or_404(station_id, db, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(models.Scenario.id == scenario_id, models.Scenario.station_id == station_id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
