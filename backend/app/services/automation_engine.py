"""Automação N1/N2 com trava de segurança.

Nenhuma reinicialização ou limpeza ocorre sem SIMULATE=false e CONFIRM_EXECUTE=true.
Em modo simulação o job descreve exatamente o que seria feito e dispara alerta simulado.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AuditLog, AutomationJob
from app.services.notifications import notify


PLAYBOOKS = {
    "clean_temp": {
        "level": "N1",
        "title": "Limpeza de pastas temporárias",
        "paths": ["C:\\Windows\\Temp", "C:\\inetpub\\temp", "/var/tmp", "/tmp"],
        "risk": "baixo",
    },
    "restart_service": {
        "level": "N1",
        "title": "Reinicialização controlada de serviço",
        "paths": [],
        "risk": "médio",
    },
    "recycle_app_pool": {
        "level": "N1",
        "title": "Recycle do Application Pool IIS",
        "paths": [],
        "risk": "médio",
    },
    "clear_cache": {
        "level": "N1",
        "title": "Limpeza de cache de aplicação",
        "paths": ["C:\\app\\cache", "/var/cache/nginx"],
        "risk": "baixo",
    },
    "analyze_db_locks": {
        "level": "N2",
        "title": "Diagnóstico de locks / sessões de banco",
        "paths": [],
        "risk": "baixo",
    },
}


class UnsafeExecutionError(RuntimeError):
    pass


def evaluate_thresholds(disk_percent: float, memory_percent: float, service_down: bool) -> list[dict]:
    settings = get_settings()
    suggestions: list[dict] = []
    if disk_percent >= settings.disk_threshold:
        suggestions.append({"action": "clean_temp", "reason": f"Disco em {disk_percent}%"})
    if memory_percent >= settings.memory_threshold:
        suggestions.append({"action": "recycle_app_pool", "reason": f"Memória em {memory_percent}%"})
    if service_down:
        suggestions.append({"action": "restart_service", "reason": "Serviço indisponível"})
    return suggestions


def _execution_allowed() -> bool:
    settings = get_settings()
    return (not settings.simulate) and settings.confirm_execute


def run_action(
    db: Session,
    action: str,
    target: str,
    support_level: str = "N1",
    requested_by: str = "operador",
) -> AutomationJob:
    if action not in PLAYBOOKS:
        raise ValueError(f"Playbook desconhecido: {action}")

    playbook = PLAYBOOKS[action]
    simulate = not _execution_allowed()
    mode = "simulate" if simulate else "execute"
    now = datetime.now(timezone.utc).isoformat()

    if not simulate:
        raise UnsafeExecutionError(
            "Execução real bloqueada neste ambiente de apresentação. "
            "Use SIMULATE=true (padrão) para demonstrar a rotina com rastreabilidade."
        )

    result = {
        "would_do": playbook["title"],
        "target": target,
        "paths": playbook["paths"],
        "risk": playbook["risk"],
        "at": now,
        "note": "Nenhum processo foi reiniciado e nenhum arquivo foi apagado.",
    }
    job = AutomationJob(
        action=action,
        target=target,
        support_level=support_level or playbook["level"],
        mode=mode,
        status="simulated",
        requested_by=requested_by,
        result=json.dumps(result, ensure_ascii=False),
        alert_sent=True,
    )
    db.add(job)
    db.add(
        AuditLog(
            actor=requested_by,
            action=action,
            entity=target,
            payload=json.dumps({"mode": mode, "playbook": playbook["title"]}, ensure_ascii=False),
        )
    )
    db.commit()
    db.refresh(job)

    notify(
        db,
        "telegram",
        f"[SIMULAR] {playbook['title']} em {target}",
        f"Playbook {action} ({job.support_level}) registrado. Modo seguro ativo.",
        extra={"job_id": job.id, "target": target},
    )
    notify(
        db,
        "slack",
        f"[SIMULAR] Automação {action}",
        f"Host {target} — sem mudança real no ambiente.",
        extra={"job_id": job.id},
    )
    return job
