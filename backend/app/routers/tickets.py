from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import TicketOut
from app.services.notifications import notify
from app.services.servicedesk import active_source
from app.services.ticket_reports import sla_metrics, weekly_report

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).order_by(Ticket.opened_at.desc()).all()


@router.get("/sla")
def sla(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return {**sla_metrics(tickets), "servicedesk": active_source()}


@router.post("/report")
def report(db: Session = Depends(get_db)):
    payload = weekly_report(db)
    notify(
        db,
        "email",
        payload["subject"],
        "Relatório semanal de SLA gerado pelo Sentinela.",
        extra={"metrics": payload["metrics"]},
    )
    return payload
