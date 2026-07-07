# ============================================================
# Pydantic schemas -- API request and response shapes
# ============================================================
# These are deliberately separate from the SQLAlchemy models in
# models.py. The DB models describe what's stored; these schemas
# describe what the API accepts and returns. Keeping them separate
# means we never accidentally leak a password_hash in a response,
# and the API contract can evolve independently of the DB schema.
# ============================================================

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# ---- Auth ---------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "farmer"   # farmer | investor -- "admin" cannot be self-assigned at
                              # registration; only an existing admin can promote a user
                              # via the admin endpoint, to prevent anyone registering
                              # themselves straight into the admin role.


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: str
    tier: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TierUpdate(BaseModel):
    tier: str  # "free" or "premium"


class RoleUpdate(BaseModel):
    role: str  # "farmer", "investor", or "admin"


# ---- Stations ------------------------------------------------

class StationCreate(BaseModel):
    name: str
    region: str
    total_hectares: float


class StationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    region: str
    total_hectares: float
    created_at: datetime


# ---- Scenarios -----------------------------------------------

class ScenarioCreate(BaseModel):
    name: str = "Untitled scenario"
    planted_hectares: float
    species: str
    density: int
    beef_price: float
    carry_capacity: float
    cattle_cartage_rate: float
    carbon_price: float
    royalty_price: float


class ScenarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    station_id: int
    name: str
    planted_hectares: float
    species: str
    density: int
    beef_price: float
    carry_capacity: float
    cattle_cartage_rate: float
    carbon_price: float
    royalty_price: float
    created_at: datetime
    updated_at: datetime | None = None


# ---- Reference data --------------------------------------------

class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    label: str
    seed_price: float
    m3_per_ha: float
    mill_name: str
    mill_km: float
    badge: str
    nursery: str
    seed_lead_time: str
    export_notes: str


class RegionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    label: str
    saleyard: str
    saleyard_km: float
    abattoir: str
    abattoir_km: float
    road_note: str
    road_risk: str
