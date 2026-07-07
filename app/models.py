# ============================================================
# SQLAlchemy ORM models -- the database schema
# ============================================================
# Four tables:
#   users             -- one row per registered person
#   stations          -- one row per station profile a user creates
#   scenarios         -- one row per saved slider/input combination
#   species_reference / region_reference
#                     -- the lookup data currently hardcoded as
#                        SPECIES and REGIONS objects in the
#                        frontend's app.js. Moving these into the
#                        database means they can be updated by an
#                        admin without redeploying the frontend.
# ============================================================

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    full_name     = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role          = Column(String, default="farmer")   # farmer | investor | admin
    tier          = Column(String, default="free")      # free | premium -- not yet enforced
                                                          # anywhere; this is a data-model
                                                          # placeholder an admin can toggle,
                                                          # ready for real restrictions/payment
                                                          # integration later.
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    stations = relationship("Station", back_populates="owner", cascade="all, delete-orphan")


class Station(Base):
    __tablename__ = "stations"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    name            = Column(String, nullable=False)
    region          = Column(String, nullable=False)   # FK-by-key to region_reference.key
    total_hectares  = Column(Float, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    owner     = relationship("User", back_populates="stations")
    scenarios = relationship("Scenario", back_populates="station", cascade="all, delete-orphan")


class Scenario(Base):
    """
    One saved snapshot of every slider/dropdown value from the
    dashboard, tied to a station. This is what lets a user close
    the browser and come back later to the exact same scenario.
    """
    __tablename__ = "scenarios"

    id          = Column(Integer, primary_key=True, index=True)
    station_id  = Column(Integer, ForeignKey("stations.id"), nullable=False)
    name        = Column(String, nullable=False, default="Untitled scenario")

    # -- Mirrors every input on the Inputs tab --
    planted_hectares    = Column(Float, nullable=False)
    species              = Column(String, nullable=False)   # FK-by-key to species_reference.key
    density               = Column(Integer, nullable=False)
    beef_price            = Column(Float, nullable=False)
    carry_capacity        = Column(Float, nullable=False)
    cattle_cartage_rate   = Column(Float, nullable=False)
    carbon_price          = Column(Float, nullable=False)
    royalty_price         = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    station = relationship("Station", back_populates="scenarios")


class SpeciesReference(Base):
    """
    Replaces the hardcoded SPECIES object in the frontend's app.js.
    'key' matches the dropdown <option value="..."> in index.html
    (e.g. 'hoop_pine', 'spotted_gum') so the frontend can swap a
    hardcoded lookup for an API call with no other changes needed.
    """
    __tablename__ = "species_reference"

    id              = Column(Integer, primary_key=True, index=True)
    key             = Column(String, unique=True, index=True, nullable=False)
    label           = Column(String, nullable=False)
    seed_price      = Column(Float, nullable=False)
    m3_per_ha       = Column(Float, nullable=False)
    mill_name       = Column(String, nullable=False)
    mill_km         = Column(Float, nullable=False)
    badge           = Column(String, nullable=False)
    nursery         = Column(String, nullable=False)
    seed_lead_time  = Column(String, nullable=False)
    export_notes    = Column(Text, nullable=False)


class RegionReference(Base):
    """
    Replaces the hardcoded REGIONS object in the frontend's app.js.
    'key' matches the dropdown <option value="..."> for #region
    (e.g. 'rockhampton', 'emerald', 'mackay', 'longreach').
    """
    __tablename__ = "region_reference"

    id            = Column(Integer, primary_key=True, index=True)
    key           = Column(String, unique=True, index=True, nullable=False)
    label         = Column(String, nullable=False)
    saleyard      = Column(String, nullable=False)
    saleyard_km   = Column(Float, nullable=False)
    abattoir      = Column(String, nullable=False)
    abattoir_km   = Column(Float, nullable=False)
    road_note     = Column(String, nullable=False)
    road_risk     = Column(String, nullable=False)  # Low | Moderate | High
