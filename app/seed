# ============================================================
# Database seed script
# ============================================================
# Populates species_reference and region_reference with exactly
# the same data currently hardcoded in the Phase 1 frontend's
# app.js (the SPECIES and REGIONS objects), so switching the
# frontend over to the API produces IDENTICAL numbers -- nothing
# changes for the user, only where the data comes from.
#
# Run once after setting up a fresh database:
#   python -m app.seed
#
# Safe to re-run -- it skips any row that already exists (matched
# by 'key'), so re-running won't create duplicates.
# ============================================================

from app.database import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)

SPECIES_DATA = [
    dict(
        key="hoop_pine", label="Hoop Pine", seed_price=1.80, m3_per_ha=280,
        mill_name="Hyne Timber -- Maryborough", mill_km=380, badge="Softwood",
        nursery="Callide Nursery, Biloela", seed_lead_time="8-12 months",
        export_notes="Hoop pine is in strong demand for structural and furniture export to "
                     "South-East Asia, particularly Vietnam and China. Gladstone Port handles "
                     "bulk timber exports. Contact Timber Queensland for broker referrals.",
    ),
    dict(
        key="spotted_gum", label="Spotted Gum", seed_price=2.20, m3_per_ha=200,
        mill_name="Masterton Timber -- Gympie", mill_km=470, badge="Hardwood",
        nursery="GreenLife Nursery, Rockhampton", seed_lead_time="6-10 months",
        export_notes="Spotted gum commands premium prices for flooring, decking and heavy "
                     "construction. Strong domestic demand in SE QLD and NSW. Export potential "
                     "to Japan and Korea via Gladstone.",
    ),
    dict(
        key="ironbark", label="Grey Ironbark", seed_price=2.10, m3_per_ha=180,
        mill_name="Mackay Timbers -- Mackay", mill_km=330, badge="Hardwood",
        nursery="Tropic Co. Nursery, Yeppoon", seed_lead_time="6-9 months",
        export_notes="Ironbark is Australia's premier hardwood for sleepers, power poles and "
                     "marine construction. High domestic demand. Export to India and the "
                     "Middle East via Gladstone or Brisbane.",
    ),
    dict(
        key="white_mahogany", label="White Mahogany", seed_price=2.40, m3_per_ha=210,
        mill_name="Martens Sawmill -- Rockhampton", mill_km=45, badge="Hardwood",
        nursery="GreenLife Nursery, Rockhampton", seed_lead_time="6-8 months",
        export_notes="White mahogany is locally milled in Rockhampton -- minimal transport "
                     "cost. Strong demand for high-end furniture and joinery. Boutique export "
                     "to Japan for premium applications.",
    ),
]

REGION_DATA = [
    dict(
        key="rockhampton", label="Rockhampton / Fitzroy",
        saleyard="CQLX Gracemere Saleyard", saleyard_km=12,
        abattoir="JBS Australia -- Rockhampton", abattoir_km=18,
        road_note="Sealed Bruce Highway access -- reliable year-round (Beef Road network)",
        road_risk="Low",
    ),
    dict(
        key="emerald", label="Emerald / Central Highlands",
        saleyard="Gracemere (via Capricorn Hwy)", saleyard_km=270,
        abattoir="JBS Australia -- Rockhampton", abattoir_km=280,
        road_note="Sealed Capricorn Highway -- some local roads unsealed and wet-season affected",
        road_risk="Moderate",
    ),
    dict(
        key="mackay", label="Mackay / Pioneer Valley",
        saleyard="Mackay Saleyards, Nebo Road", saleyard_km=35,
        abattoir="Borthwicks Mackay (processing via Rockhampton)", abattoir_km=330,
        road_note="Sealed Bruce Highway -- minor wet-season disruption risk",
        road_risk="Low",
    ),
    dict(
        key="longreach", label="Longreach / Central West",
        saleyard="Blackall Saleyards", saleyard_km=210,
        abattoir="JBS Australia -- Rockhampton", abattoir_km=690,
        road_note="Sealed Landsborough/Capricorn Hwy -- long haul, gravel station access roads common",
        road_risk="High",
    ),
]


def seed():
    db = SessionLocal()
    try:
        added_species = 0
        for row in SPECIES_DATA:
            if not db.query(models.SpeciesReference).filter_by(key=row["key"]).first():
                db.add(models.SpeciesReference(**row))
                added_species += 1

        added_regions = 0
        for row in REGION_DATA:
            if not db.query(models.RegionReference).filter_by(key=row["key"]).first():
                db.add(models.RegionReference(**row))
                added_regions += 1

        db.commit()
        print(f"Seed complete -- added {added_species} species, {added_regions} regions "
              f"(existing rows were left untouched).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
