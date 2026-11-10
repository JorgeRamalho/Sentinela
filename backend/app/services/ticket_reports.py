"""Métricas de SLA e relatório semanal de Service Desk."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Ticket


OPEN_STATUSES = {"open", "in_progress", "pending"}
CLOSED_STATUSES = {"resolved", "closed"}


def sla_metrics(tickets: list[Ticket]) -> dict:
    total = len(tickets)
    opened = [item for item in tickets if item.status in OPEN_STATUSES]
    closed = [item for item in tickets if item.status in CLOSED_STATUSES]
    responses = [item.first_response_minutes for item in tickets if item.first_response_minutes is not None]
    resolutions = [item.resolution_minutes for item in tickets if item.resolution_minutes is not None]
    breaches = [
        item
        for item in tickets
        if item.resolution_minutes is not None and item.resolution_minutes > item.sla_minutes
    ]
    by_priority = Counter(item.priority for item in tickets)
    by_source = Counter(item.source for item in tickets)

    def avg(values: list[int]) -> float:
        return round(sum(values) / len(values), 1) if values else 0.0

    compliance = round((1 - (len(breaches) / total)) * 100, 1) if total else 100.0
    return {
        "total": total,
        "open": len(opened),
        "closed": len(closed),
        "avg_first_response_minutes": avg(responses),
        "avg_resolution_minutes": avg(resolutions),
        "sla_breaches": len(breaches),
        "sla_compliance_percent": compliance,
        "by_priority": dict(by_priority),
        "by_source": dict(by_source),
    }


def weekly_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    current = now or datetime.now(timezone.utc)
    start = current - timedelta(days=7)
    return start, current


def weekly_report(db: Session) -> dict:
    start, end = weekly_window()
    tickets = db.query(Ticket).all()
    metrics = sla_metrics(tickets)
    hottest = sorted(
        [item for item in tickets if item.status in OPEN_STATUSES],
        key=lambda item: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item.priority, 9),
    )[:5]
    html = _render_email(metrics, hottest)
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "metrics": metrics,
        "open_priority": [
            {"number": item.number, "title": item.title, "priority": item.priority, "assignee": item.assignee}
            for item in hottest
        ],
        "email_html": html,
        "subject": "Sentinela — relatório semanal de chamados (SLA)",
    }


def _render_email(metrics: dict, hottest: list[Ticket]) -> str:
    rows = "".join(
        f"<li>{item.number} · {item.title} ({item.priority})</li>" for item in hottest
    ) or "<li>Nenhum chamado aberto de alta prioridade.</li>"
    return f"""
    <h2>Relatório semanal de Service Desk</h2>
    <p>Abertos: {metrics['open']} · Fechados: {metrics['closed']} · SLA: {metrics['sla_compliance_percent']}%</p>
    <p>TMA (resolução): {metrics['avg_resolution_minutes']} min · 1ª resposta: {metrics['avg_first_response_minutes']} min</p>
    <p>Violações de SLA: {metrics['sla_breaches']}</p>
    <h3>Fila crítica</h3>
    <ul>{rows}</ul>
    <p>Gerado pelo Sentinela em modo seguro (SIMULAR).</p>
    """
