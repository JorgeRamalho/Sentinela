import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident, KnowledgeArticle, LogEvent, Ticket
from app.schemas import IncidentOut
from app.services.correlator import correlate

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/{code}")
def get_incident(code: str, db: Session = Depends(get_db)):
    item = db.query(Incident).filter(Incident.code == code.upper()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Incidente não encontrado")
    return IncidentOut.model_validate(item)


@router.post("/{code}/correlate")
def correlate_incident(code: str, db: Session = Depends(get_db)):
    item = db.query(Incident).filter(Incident.code == code.upper()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Incidente não encontrado")
    evidence = correlate(
        item,
        db.query(LogEvent).all(),
        db.query(Ticket).all(),
        db.query(KnowledgeArticle).all(),
    )
    item.evidence = json.dumps(evidence, ensure_ascii=False)
    if item.status == "open":
        item.status = "investigating"
    db.commit()
    return evidence
