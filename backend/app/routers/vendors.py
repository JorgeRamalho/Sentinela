from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DatabaseInstance, KnowledgeArticle, Vendor
from app.schemas import VendorOut

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


@router.get("", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()


@router.get("/{vendor_id}")
def vendor_detail(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    articles = db.query(KnowledgeArticle).filter(KnowledgeArticle.vendor_id == vendor_id).all()
    databases = db.query(DatabaseInstance).filter(DatabaseInstance.vendor_id == vendor_id).all()
    return {
        "vendor": VendorOut.model_validate(vendor) if vendor else None,
        "articles": [{"code": item.code, "title": item.title, "level": item.support_level} for item in articles],
        "databases": [{"name": item.name, "status": item.status} for item in databases],
    }
