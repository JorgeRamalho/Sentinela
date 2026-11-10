from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import automation, dashboard, databases, incidents, knowledge, logs, monitoring, tickets, vendors
from app.schemas import MetaOut
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(
    title="Sentinela API",
    description="Plataforma de sustentação N1/N2 — monitoramento, incidentes, automação e base de conhecimento.",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(monitoring.router)
app.include_router(incidents.router)
app.include_router(tickets.router)
app.include_router(logs.router)
app.include_router(automation.router)
app.include_router(databases.router)
app.include_router(vendors.router)
app.include_router(knowledge.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name, "simulate": settings.simulate}


@app.get("/api/meta", response_model=MetaOut)
def meta():
    return MetaOut(
        app=settings.app_name,
        version=__version__,
        env=settings.app_env,
        simulate=settings.simulate,
        confirm_execute=settings.confirm_execute,
    )
