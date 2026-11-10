"""Correlação de evidências: logs, métricas, chamados e artigos da base."""

from __future__ import annotations

from app.models import Incident, KnowledgeArticle, LogEvent, Ticket

KEYWORD_HINTS = (
    ("ORA-", "oracle", "banco"),
    ("w3wp", "iis", "memoria"),
    ("OutOfMemory", "memoria", "iis"),
    ("disk", "disco", "temp"),
    ("LDAP", "autenticacao", "rede"),
    ("timeout", "integracao", "totvs"),
    ("SSL", "certificado", "https"),
    ("backup", "backup", "storage"),
    ("NullPointer", "aplicacao", "faturamento"),
    ("FATAL", "critico", "aplicacao"),
)


def _haystack(incident: Incident) -> str:
    return f"{incident.title} {incident.description} {incident.host} {incident.source}".lower()


def correlate(
    incident: Incident,
    logs: list[LogEvent],
    tickets: list[Ticket],
    articles: list[KnowledgeArticle],
) -> dict:
    blob = _haystack(incident)
    keywords = [hint[0].lower() for hint in KEYWORD_HINTS if hint[0].lower() in blob]
    extra = [token for _, *rest in KEYWORD_HINTS for token in rest if token in blob]
    terms = set(keywords + extra + [incident.host.lower()])

    related_logs = []
    for event in logs:
        text = f"{event.host} {event.message}".lower()
        score = sum(1 for term in terms if term and term in text)
        if incident.host and incident.host.lower() in event.host.lower():
            score += 2
        if score:
            related_logs.append({"id": event.id, "level": event.level, "message": event.message[:240], "score": score})
    related_logs.sort(key=lambda item: item["score"], reverse=True)

    related_tickets = []
    for ticket in tickets:
        text = f"{ticket.title} {ticket.number}".lower()
        score = sum(1 for term in terms if term and term in text)
        if score:
            related_tickets.append({"id": ticket.id, "number": ticket.number, "title": ticket.title, "score": score})
    related_tickets.sort(key=lambda item: item["score"], reverse=True)

    suggested_kb = []
    for article in articles:
        text = f"{article.title} {article.tags} {article.symptoms}".lower()
        score = sum(1 for term in terms if term and term in text)
        if score:
            suggested_kb.append(
                {"id": article.id, "code": article.code, "title": article.title, "level": article.support_level, "score": score}
            )
    suggested_kb.sort(key=lambda item: item["score"], reverse=True)

    confidence = min(99, 35 + 12 * len(related_logs[:3]) + 10 * len(related_tickets[:2]) + 8 * len(suggested_kb[:2]))
    level = "N2" if any(token in blob for token in ("oracle", "lock", "dump", "deadlock")) else incident.support_level
    return {
        "incident": incident.code,
        "confidence": confidence,
        "suggested_level": level,
        "related_logs": related_logs[:6],
        "related_tickets": related_tickets[:5],
        "suggested_kb": suggested_kb[:4],
        "next_action": "Aplicar runbook sugerido em modo SIMULAR e registrar evidência no chamado.",
    }
