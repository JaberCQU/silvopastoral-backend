# ============================================================
# Admin routes -- user management, role/tier control
# ============================================================
# Every route here is protected by require_admin, which checks
# the logged-in user's role == 'admin'. There is no way to become
# an admin through self-service registration (see auth.py's
# register() route) -- the first admin must be promoted manually,
# either directly in the database or via a one-time script.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[schemas.UserOut])
def list_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Admin-only: list every registered user, regardless of who created them."""
    return db.query(models.User).all()


@router.put("/users/{user_id}/tier", response_model=schemas.UserOut)
def set_user_tier(
    user_id: int,
    payload: schemas.TierUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Admin-only: toggle a user's tier between 'free' and 'premium'.
    Not yet enforced anywhere in the app -- this is the data-model
    and admin-control piece, ready for real feature-gating or
    payment integration later."""
    if payload.tier not in ("free", "premium"):
        raise HTTPException(status_code=400, detail="tier must be 'free' or 'premium'")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = payload.tier
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/role", response_model=schemas.UserOut)
def set_user_role(
    user_id: int,
    payload: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Admin-only: change a user's role, including promoting someone
    to admin. This is the ONLY way a user can become an admin --
    self-registration can never set role='admin' (see auth.py)."""
    if payload.role not in ("farmer", "investor", "admin"):
        raise HTTPException(status_code=400, detail="role must be 'farmer', 'investor', or 'admin'")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Admin-only: delete a user and (via cascade) all their stations
    and scenarios. An admin cannot delete their own account through
    this endpoint, to avoid accidentally locking everyone out."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account from here")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()


@router.get("/stations", response_model=List[schemas.StationOut])
def list_all_stations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Admin-only: list every station across every user, for
    moderation/oversight purposes."""
    return db.query(models.Station).all()
