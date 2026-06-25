# ============================================================
# Station routes -- CRUD for a user's station profiles
# ============================================================
# All routes here require a valid logged-in user (get_current_user),
# and every query is filtered by that user's ID, so one user can
# never see or modify another user's stations.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/stations", tags=["stations"])


@router.post("", response_model=schemas.StationOut, status_code=status.HTTP_201_CREATED)
def create_station(
    payload: schemas.StationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    station = models.Station(**payload.model_dump(), user_id=current_user.id)
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


@router.get("", response_model=List[schemas.StationOut])
def list_my_stations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Station).filter(models.Station.user_id == current_user.id).all()


def _get_owned_station_or_404(station_id: int, db: Session, current_user: models.User) -> models.Station:
    station = (
        db.query(models.Station)
        .filter(models.Station.id == station_id, models.Station.user_id == current_user.id)
        .first()
    )
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("/{station_id}", response_model=schemas.StationOut)
def get_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return _get_owned_station_or_404(station_id, db, current_user)


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    station = _get_owned_station_or_404(station_id, db, current_user)
    db.delete(station)
    db.commit()
