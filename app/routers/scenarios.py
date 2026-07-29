# ============================================================
# Scenario routes -- CRUD for saved dashboard input snapshots
# Updated: investors can read scenarios from ANY station,
# admins can read/write scenarios from ANY station,
# farmers can only access their own stations' scenarios.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/stations/{station_id}/scenarios", tags=["scenarios"])


def _get_accessible_station_or_404(
    station_id: int, db: Session, current_user: models.User
) -> models.Station:
    """
    Returns the station if the current user can access it.
    - Investors and admins: can access ANY station
    - Farmers: can only access their own stations
    """
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    if current_user.role not in ("investor", "admin"):
        if station.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Station not found")
    return station


def _require_write_access(station: models.Station, current_user: models.User):
    """Raises 403 if the user cannot modify scenarios on this station."""
    if current_user.role == "investor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investors have read-only access to scenarios."
        )
    if current_user.role == "admin":
        return  # admins can write to any station
    if station.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Station not found")


@router.post("", response_model=schemas.ScenarioOut, status_code=status.HTTP_201_CREATED)
def create_scenario(
    station_id: int,
    payload: schemas.ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    station = _get_accessible_station_or_404(station_id, db, current_user)
    _require_write_access(station, current_user)
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
    _get_accessible_station_or_404(station_id, db, current_user)
    return db.query(models.Scenario).filter(
        models.Scenario.station_id == station_id
    ).all()


@router.get("/{scenario_id}", response_model=schemas.ScenarioOut)
def get_scenario(
    station_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_accessible_station_or_404(station_id, db, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(
            models.Scenario.id == scenario_id,
            models.Scenario.station_id == station_id
        )
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
    station = _get_accessible_station_or_404(station_id, db, current_user)
    _require_write_access(station, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(
            models.Scenario.id == scenario_id,
            models.Scenario.station_id == station_id
        )
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
    station = _get_accessible_station_or_404(station_id, db, current_user)
    _require_write_access(station, current_user)
    scenario = (
        db.query(models.Scenario)
        .filter(
            models.Scenario.id == scenario_id,
            models.Scenario.station_id == station_id
        )
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
