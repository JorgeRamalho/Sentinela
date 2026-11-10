import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SIMULATE"] = "true"
os.environ["CONFIRM_EXECUTE"] = "false"
os.environ["LOG_SCAN_PATH"] = str(ROOT / "data" / "logs")
os.environ["EXPORT_PATH"] = str(ROOT / "data" / "exports")

from app.config import get_settings

get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Vendor
from app.seed import seed_if_empty


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        assert db.query(Vendor).count() >= 1
    finally:
        db.close()
    yield


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
