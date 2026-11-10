"""Conectores de Service Desk.

Na demo os chamados já vêm do seed (GLPI, Jira, ServiceNow, Zendesk).
Se as variáveis de ambiente do fornecedor estiverem preenchidas, o esqueleto abaixo
é o ponto de extensão para a API real — sem misturar credenciais no código.
"""

from __future__ import annotations

from app.config import get_settings


def active_source() -> dict:
    settings = get_settings()
    source = settings.ticket_source.lower()
    live = {
        "jira": bool(settings.jira_url and settings.jira_token),
        "glpi": bool(settings.glpi_url and settings.glpi_app_token),
        "servicenow": bool(settings.servicenow_url and settings.servicenow_user),
        "zendesk": bool(settings.zendesk_subdomain and settings.zendesk_token),
    }
    return {
        "configured": source,
        "live": live.get(source, False),
        "mode": "api" if live.get(source) else "simulated-feed",
        "sources": live,
    }
