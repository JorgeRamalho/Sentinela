"""Coleta de métricas reais do host local + fazenda simulada de sustentação."""

from __future__ import annotations

from datetime import datetime, timezone

import psutil


FARM = (
    {"host": "SRV-APP-01", "cpu": 31.4, "memory": 62.0, "disk": 71.2, "role": "aplicacao"},
    {"host": "SRV-APP-02", "cpu": 78.9, "memory": 93.4, "disk": 96.1, "role": "aplicacao"},
    {"host": "SRV-WEB-01", "cpu": 44.0, "memory": 70.2, "disk": 58.0, "role": "iis"},
    {"host": "SRV-DB-ORACLE", "cpu": 66.2, "memory": 81.5, "disk": 74.8, "role": "banco"},
    {"host": "SRV-FILE-01", "cpu": 12.0, "memory": 40.1, "disk": 88.4, "role": "storage"},
)


def local_metrics() -> dict:
    disk = psutil.disk_usage("C:\\" if psutil.WINDOWS else "/")
    return {
        "host": "LOCAL-CONSOLE",
        "cpu_percent": round(psutil.cpu_percent(interval=0.15), 1),
        "memory_percent": round(psutil.virtual_memory().percent, 1),
        "disk_percent": round(disk.percent, 1),
        "role": "console",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "real": True,
    }


def farm_metrics() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    payload = [
        {
            "host": item["host"],
            "cpu_percent": item["cpu"],
            "memory_percent": item["memory"],
            "disk_percent": item["disk"],
            "role": item["role"],
            "collected_at": now,
            "real": False,
        }
        for item in FARM
    ]
    payload.insert(0, local_metrics())
    return payload


def health_status(cpu: float, memory: float, disk: float) -> str:
    if disk >= 95 or memory >= 95 or cpu >= 95:
        return "critical"
    if disk >= 88 or memory >= 90 or cpu >= 85:
        return "warning"
    return "healthy"
