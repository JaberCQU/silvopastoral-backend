from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])

# One-time admin bootstrap endpoint. DELETE THIS FILE after use.
BOOTSTRAP_SECRET = "silvopastoral-bootstrap-2026"

@router.post("/promote-admin")
def bootstrap_admin(secret: str, email: str, db: Session = Depends(get_db)):
    if secret != BOOTSTRAP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "admin"
    db.commit()
    return {"message": f"Promoted {email} to admin"}
