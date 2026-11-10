from datetime import datetime

from pydantic import BaseModel, Field


class MetaOut(BaseModel):
    app: str
    version: str
    env: str
    simulate: bool
    confirm_execute: bool


class IncidentOut(BaseModel):
    id: int
    code: str
    title: str
    description: str
    severity: str
    status: str
    source: str
    host: str
    evidence: str
    support_level: str
    ticket_id: int | None
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class TicketOut(BaseModel):
    id: int
    number: str
    title: str
    requester: str
    priority: str
    status: str
    source: str
    sla_minutes: int
    first_response_minutes: int | None
    resolution_minutes: int | None
    opened_at: datetime
    closed_at: datetime | None
    assignee: str

    model_config = {"from_attributes": True}


class AutomationRunIn(BaseModel):
    action: str = Field(..., examples=["clean_temp", "restart_service", "recycle_app_pool"])
    target: str = Field(..., examples=["SRV-APP-02"])
    support_level: str = "N1"
    requested_by: str = "operador"


class KnowledgeOut(BaseModel):
    id: int
    code: str
    title: str
    category: str
    symptoms: str
    diagnosis: str
    resolution: str
    tags: str
    support_level: str
    vendor_id: int | None

    model_config = {"from_attributes": True}


class VendorOut(BaseModel):
    id: int
    name: str
    category: str
    contact: str
    sla_hours: int
    contract_until: str
    status: str
    notes: str

    model_config = {"from_attributes": True}


class DatabaseOut(BaseModel):
    id: int
    name: str
    engine: str
    host: str
    port: int
    status: str
    connections: int
    max_connections: int
    latency_ms: int
    vendor_id: int | None
    role: str

    model_config = {"from_attributes": True}
