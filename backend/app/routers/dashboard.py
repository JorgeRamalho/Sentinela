import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Alert, AutomationJob, DatabaseInstance, Incident, Ticket
from app.services.monitoring import farm_metrics, health_status
from app.services.ticket_reports import sla_metrics

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    settings = get_settings()
    incidents = db.query(Incident).all()
    tickets = db.query(Ticket).all()
    jobs = db.query(AutomationJob).order_by(AutomationJob.created_at.desc()).limit(6).all()
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(6).all()
    databases = db.query(DatabaseInstance).all()
    metrics = farm_metrics()
    open_incidents = [item for item in incidents if item.status in {"open", "investigating"}]
    return {
        "meta": {"simulate": settings.simulate, "env": settings.app_env},
        "kpis": {
            "open_incidents": len(open_incidents),
            "critical_incidents": len([item for item in open_incidents if item.severity == "critical"]),
            "open_tickets": len([item for item in tickets if item.status in {"open", "in_progress", "pending"}]),
            "databases_degraded": len([item for item in databases if item.status != "healthy"]),
            "sla": sla_metrics(tickets),
        },
        "hosts": [
            {**item, "status": health_status(item["cpu_percent"], item["memory_percent"], item["disk_percent"])}
            for item in metrics
        ],
        "recent_jobs": [
            {"id": job.id, "action": job.action, "target": job.target, "status": job.status, "mode": job.mode}
            for job in jobs
        ],
        "recent_alerts": [
            {"id": item.id, "channel": item.channel, "title": item.title, "simulated": item.simulated}
            for item in alerts
        ],
        "priority_incidents": [
            {
                "code": item.code,
                "title": item.title,
                "severity": item.severity,
                "host": item.host,
                "level": item.support_level,
                "status": item.status,
            }
            for item in sorted(open_incidents, key=lambda row: row.severity)[:5]
        ],
        "audit_hint": json.dumps({"simulate": settings.simulate}),
    }
