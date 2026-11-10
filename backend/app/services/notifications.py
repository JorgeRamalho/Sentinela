"""Alertas Telegram/Slack com modo SIMULAR obrigatório por padrão."""

from __future__ import annotations

import json

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Alert, AuditLog


def _store(db: Session, channel: str, title: str, payload: dict, simulated: bool) -> Alert:
    alert = Alert(
        channel=channel,
        title=title,
        payload=json.dumps(payload, ensure_ascii=False),
        simulated=simulated,
    )
    db.add(alert)
    db.add(
        AuditLog(
            actor="sentinela",
            action="notify",
            entity=channel,
            payload=json.dumps({"title": title, "simulated": simulated}, ensure_ascii=False),
        )
    )
    db.commit()
    db.refresh(alert)
    return alert


def notify(db: Session, channel: str, title: str, body: str, extra: dict | None = None) -> dict:
    settings = get_settings()
    payload = {"title": title, "body": body, **(extra or {})}
    must_simulate = settings.simulate or channel == "email" and not settings.smtp_host

    if channel == "telegram":
        if must_simulate or not settings.telegram_bot_token:
            alert = _store(db, "telegram", title, payload, simulated=True)
            return {"status": "simulated", "channel": "telegram", "id": alert.id}
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        httpx.post(url, json={"chat_id": settings.telegram_chat_id, "text": f"{title}\n{body}"}, timeout=10)
        alert = _store(db, "telegram", title, payload, simulated=False)
        return {"status": "sent", "channel": "telegram", "id": alert.id}

    if channel == "slack":
        if must_simulate or not settings.slack_webhook_url:
            alert = _store(db, "slack", title, payload, simulated=True)
            return {"status": "simulated", "channel": "slack", "id": alert.id}
        httpx.post(settings.slack_webhook_url, json={"text": f"*{title}*\n{body}"}, timeout=10)
        alert = _store(db, "slack", title, payload, simulated=False)
        return {"status": "sent", "channel": "slack", "id": alert.id}

    if channel == "email":
        alert = _store(db, "email", title, payload, simulated=True)
        return {"status": "simulated", "channel": "email", "id": alert.id, "to": settings.report_email_to}

    raise ValueError(f"Canal não suportado: {channel}")
