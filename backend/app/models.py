from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    contact: Mapped[str] = mapped_column(String(160))
    sla_hours: Mapped[int] = mapped_column(Integer, default=4)
    contract_until: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(40), default="ativo")
    notes: Mapped[str] = mapped_column(Text, default="")

    databases: Mapped[list["DatabaseInstance"]] = relationship(back_populates="vendor")
    articles: Mapped[list["KnowledgeArticle"]] = relationship(back_populates="vendor")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default=Severity.HIGH.value)
    status: Mapped[str] = mapped_column(String(30), default=IncidentStatus.OPEN.value)
    source: Mapped[str] = mapped_column(String(80), default="monitor")
    host: Mapped[str] = mapped_column(String(80), default="")
    evidence: Mapped[str] = mapped_column(Text, default="{}")
    support_level: Mapped[str] = mapped_column(String(8), default="N1")
    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(40), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    requester: Mapped[str] = mapped_column(String(120))
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default=TicketStatus.OPEN.value)
    source: Mapped[str] = mapped_column(String(40), default="glpi")
    sla_minutes: Mapped[int] = mapped_column(Integer, default=240)
    first_response_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assignee: Mapped[str] = mapped_column(String(80), default="fila-n1")


class LogScan(Base):
    __tablename__ = "log_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    files_scanned: Mapped[int] = mapped_column(Integer, default=0)
    errors_found: Mapped[int] = mapped_column(Integer, default=0)
    output_json: Mapped[str] = mapped_column(String(260), default="")
    output_csv: Mapped[str] = mapped_column(String(260), default="")
    summary: Mapped[str] = mapped_column(Text, default="{}")


class LogEvent(Base):
    __tablename__ = "log_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int | None] = mapped_column(ForeignKey("log_scans.id"), nullable=True)
    source_file: Mapped[str] = mapped_column(String(260))
    host: Mapped[str] = mapped_column(String(80), default="")
    level: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[str] = mapped_column(String(40), default="")
    line_number: Mapped[int] = mapped_column(Integer, default=0)


class AutomationJob(Base):
    __tablename__ = "automation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(120))
    support_level: Mapped[str] = mapped_column(String(8), default="N1")
    mode: Mapped[str] = mapped_column(String(20), default="simulate")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    requested_by: Mapped[str] = mapped_column(String(80), default="operador")
    result: Mapped[str] = mapped_column(Text, default="{}")
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    host: Mapped[str] = mapped_column(String(80))
    cpu_percent: Mapped[float] = mapped_column(Float)
    memory_percent: Mapped[float] = mapped_column(Float)
    disk_percent: Mapped[float] = mapped_column(Float)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MonitoredService(Base):
    __tablename__ = "monitored_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    host: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="up")
    pid: Mapped[str] = mapped_column(String(20), default="")
    last_check: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    message: Mapped[str] = mapped_column(String(200), default="")


class DatabaseInstance(Base):
    __tablename__ = "database_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    engine: Mapped[str] = mapped_column(String(40))
    host: Mapped[str] = mapped_column(String(80))
    port: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="healthy")
    connections: Mapped[int] = mapped_column(Integer, default=0)
    max_connections: Mapped[int] = mapped_column(Integer, default=200)
    latency_ms: Mapped[int] = mapped_column(Integer, default=12)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(40), default="prod")

    vendor: Mapped[Vendor | None] = relationship(back_populates="databases")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(80))
    symptoms: Mapped[str] = mapped_column(Text)
    diagnosis: Mapped[str] = mapped_column(Text)
    resolution: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(200), default="")
    support_level: Mapped[str] = mapped_column(String(8), default="N1")
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), nullable=True)

    vendor: Mapped[Vendor | None] = relationship(back_populates="articles")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(80))
    entity: Mapped[str] = mapped_column(String(80))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(200))
    payload: Mapped[str] = mapped_column(Text)
    simulated: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
