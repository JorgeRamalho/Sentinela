from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import KnowledgeArticle
from app.schemas import KnowledgeOut

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeOut])
def list_articles(q: str | None = None, db: Session = Depends(get_db)):
    rows = db.query(KnowledgeArticle).all()
    if q:
        needle = q.lower()
        rows = [
            item
            for item in rows
            if needle in f"{item.title} {item.tags} {item.symptoms} {item.resolution} {item.code}".lower()
        ]
    return rows
