# ============================================================
# Station routes -- final version with owner_email included
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/stations", tags=["stations"])


def _station_to_out(station: models.Station, db: Session) -> dict:
    """Convert a station ORM object to a dict including the owner's email."""
    owner = db.query(models.User).filter(models.User.id == station.user_id).first()
    return {
        "id": station.id,
        "user_id": station.user_id,
        "name": station.name,
        "region": station.region,
        "total_hectares": station.total_hectares,
        "created_at": station.created_at,
        "owner_email": owner.email if owner else "",
    }


@router.post("", response_model=schemas.StationOut, status_code=status.HTTP_201_CREATED)
def create_station(
    payload: schemas.StationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role == "investor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investors cannot create stations."
        )
    station = models.Station(**payload.model_dump(), user_id=current_user.id)
    db.add(station)
    db.commit()
    db.refresh(station)
    return _station_to_out(station, db)


@router.get("", response_model=List[schemas.StationOut])
def list_stations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role in ("investor", "admin"):
        stations = db.query(models.Station).all()
    else:
        stations = db.query(models.Station).filter(
            models.Station.user_id == current_user.id
        ).all()
    return [_station_to_out(s, db) for s in stations]


def _get_station_or_404(station_id: int, db: Session) -> models.Station:
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


def _require_write_access(station: models.Station, current_user: models.User):
    if current_user.role == "investor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investors have read-only access to stations."
        )
    if current_user.role == "admin":
        return
    if station.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Station not found")


@router.get("/{station_id}", response_model=schemas.StationOut)
def get_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    station = _get_station_or_404(station_id, db)
    if current_user.role not in ("investor", "admin"):
        if station.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Station not found")
    return _station_to_out(station, db)


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    station = _get_station_or_404(station_id, db)
    _require_write_access(station, current_user)
    db.delete(station)
    db.commit()
