import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Alert, AuditLog, AutomationJob
from app.schemas import AutomationRunIn
from app.services.automation_engine import PLAYBOOKS, UnsafeExecutionError, run_action

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.get("/playbooks")
def playbooks():
    settings = get_settings()
    return {
        "simulate": settings.simulate,
        "confirm_execute": settings.confirm_execute,
        "playbooks": [{"id": key, **value} for key, value in PLAYBOOKS.items()],
    }


@router.get("/jobs")
def jobs(db: Session = Depends(get_db)):
    rows = db.query(AutomationJob).order_by(AutomationJob.created_at.desc()).limit(50).all()
    return [
        {
            "id": item.id,
            "action": item.action,
            "target": item.target,
            "support_level": item.support_level,
            "mode": item.mode,
            "status": item.status,
            "requested_by": item.requested_by,
            "result": json.loads(item.result or "{}"),
            "alert_sent": item.alert_sent,
            "created_at": item.created_at.isoformat(),
        }
        for item in rows
    ]


@router.post("/run")
def run(payload: AutomationRunIn, db: Session = Depends(get_db)):
    try:
        job = run_action(db, payload.action, payload.target, payload.support_level, payload.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UnsafeExecutionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "id": job.id,
        "status": job.status,
        "mode": job.mode,
        "result": json.loads(job.result),
    }


@router.get("/audit")
def audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(40).all()
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(20).all()
    return {
        "audit": [
            {
                "id": item.id,
                "actor": item.actor,
                "action": item.action,
                "entity": item.entity,
                "payload": json.loads(item.payload or "{}"),
                "created_at": item.created_at.isoformat(),
            }
            for item in rows
        ],
        "alerts": [
            {
                "id": item.id,
                "channel": item.channel,
                "title": item.title,
                "simulated": item.simulated,
                "created_at": item.created_at.isoformat(),
            }
            for item in alerts
        ],
    }
