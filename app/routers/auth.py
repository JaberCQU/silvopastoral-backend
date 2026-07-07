# ============================================================
# Auth routes: POST /auth/register, POST /auth/login
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    # Security: regardless of what role the client sends, registration
    # can only ever create a "farmer" or "investor" account. The admin
    # role can ONLY be granted by an existing admin via the
    # PUT /admin/users/{id}/role endpoint -- this stops anyone from
    # registering themselves straight into admin access by simply
    # sending {"role": "admin"} in the request body.
    safe_role = payload.role if payload.role in ("farmer", "investor") else "farmer"

    user = models.User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=auth.hash_password(payload.password),
        role=safe_role,
        tier="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Uses OAuth2PasswordRequestForm so this endpoint works directly
    with FastAPI's auto-generated /docs "Authorize" button, and with
    standard frontend form-encoded login requests (username=email).
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    """Returns the logged-in user's own profile. Useful for the frontend
    to check 'am I logged in, and as whom' on page load."""
    return current_user
