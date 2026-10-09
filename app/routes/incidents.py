from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(resolved: Optional[bool] = None, db: Session = Depends(get_db)):
    q = db.query(models.Incident)
    if resolved is not None:
        q = q.filter(models.Incident.resolved == (1 if resolved else 0))
    return q.order_by(models.Incident.timestamp.desc()).all()


@router.post("/", response_model=schemas.IncidentOut)
def create_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db)):
    """Manually log an incident (e.g. accident report, road closure)."""
    incident = models.Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.patch("/{incident_id}/resolve", response_model=schemas.IncidentOut)
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.resolved = 1
    db.commit()
    db.refresh(incident)
    return incident
