from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MetricSnapshot, MonitoredService
from app.services.automation_engine import evaluate_thresholds
from app.services.monitoring import farm_metrics, health_status

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    snapshot = farm_metrics()
    for item in snapshot:
        db.add(
            MetricSnapshot(
                host=item["host"],
                cpu_percent=item["cpu_percent"],
                memory_percent=item["memory_percent"],
                disk_percent=item["disk_percent"],
            )
        )
    db.commit()
    return {
        "hosts": [
            {
                **item,
                "status": health_status(item["cpu_percent"], item["memory_percent"], item["disk_percent"]),
                "suggestions": evaluate_thresholds(
                    item["disk_percent"],
                    item["memory_percent"],
                    False,
                ),
            }
            for item in snapshot
        ]
    }


@router.get("/services")
def services(db: Session = Depends(get_db)):
    rows = db.query(MonitoredService).all()
    return {
        "services": [
            {
                "id": item.id,
                "name": item.name,
                "host": item.host,
                "status": item.status,
                "pid": item.pid,
                "message": item.message,
                "last_check": item.last_check.isoformat(),
            }
            for item in rows
        ]
    }
