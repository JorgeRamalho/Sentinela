from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DatabaseInstance, Vendor
from app.schemas import DatabaseOut

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("", response_model=list[DatabaseOut])
def list_databases(db: Session = Depends(get_db)):
    return db.query(DatabaseInstance).all()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    rows = db.query(DatabaseInstance).all()
    vendors = {item.id: item.name for item in db.query(Vendor).all()}
    return {
        "instances": [
            {
                "name": item.name,
                "engine": item.engine,
                "host": item.host,
                "status": item.status,
                "fill": round((item.connections / item.max_connections) * 100, 1),
                "latency_ms": item.latency_ms,
                "vendor": vendors.get(item.vendor_id, "interno"),
                "role": item.role,
                "signal": "Sessões no limite — correlacionar com INC-1043"
                if item.status == "degraded"
                else "Dentro da linha de base",
            }
            for item in rows
        ]
    }
