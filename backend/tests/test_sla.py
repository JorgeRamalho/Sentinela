from datetime import datetime, timezone

from app.models import Ticket
from app.services.ticket_reports import sla_metrics


def test_sla_open_vs_closed_and_breach():
    now = datetime.now(timezone.utc)
    tickets = [
        Ticket(number="A", title="a", requester="x", priority="high", status="open", sla_minutes=60, first_response_minutes=10, opened_at=now),
        Ticket(number="B", title="b", requester="x", priority="low", status="closed", sla_minutes=60, first_response_minutes=5, resolution_minutes=40, opened_at=now),
        Ticket(number="C", title="c", requester="x", priority="critical", status="resolved", sla_minutes=60, first_response_minutes=8, resolution_minutes=180, opened_at=now),
    ]
    metrics = sla_metrics(tickets)
    assert metrics["total"] == 3
    assert metrics["open"] == 1
    assert metrics["closed"] == 2
    assert metrics["sla_breaches"] == 1
    assert metrics["avg_first_response_minutes"] == 7.7
    assert metrics["sla_compliance_percent"] < 100
