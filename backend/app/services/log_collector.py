"""Coletor e limpador de logs de erro (N1/N2).

Varre diretórios, mantém apenas ERROR / FATAL / Exception / CRITICAL
e exporta um resumo limpo em CSV ou JSON.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CRITICAL_PATTERNS = (
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bFATAL\b", re.IGNORECASE),
    re.compile(r"\bCRITICAL\b", re.IGNORECASE),
    re.compile(r"Exception"),
    re.compile(r"\bORA-\d{5}\b"),
    re.compile(r"\bOutOfMemory\b", re.IGNORECASE),
)

LEVEL_PATTERN = re.compile(r"\b(ERROR|FATAL|CRITICAL|WARN|WARNING|INFO|DEBUG|Exception)\b", re.IGNORECASE)
TS_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:,\d+)?")
HOST_PATTERN = re.compile(r"\b(SRV-[A-Z0-9-]+|db-\w+|app-\w+|web-\w+)\b", re.IGNORECASE)


@dataclass
class LogRecord:
    source_file: str
    host: str
    level: str
    message: str
    timestamp: str
    line_number: int


def is_critical(line: str) -> bool:
    return any(pattern.search(line) for pattern in CRITICAL_PATTERNS)


def classify_level(line: str) -> str:
    match = LEVEL_PATTERN.search(line)
    if not match:
        return "ERROR"
    token = match.group(1).upper()
    if token == "WARNING":
        return "WARN"
    if token == "EXCEPTION":
        return "Exception"
    return token


def parse_line(path: Path, line_number: int, line: str) -> LogRecord:
    ts_match = TS_PATTERN.search(line)
    host_match = HOST_PATTERN.search(line)
    return LogRecord(
        source_file=path.name,
        host=(host_match.group(1).upper() if host_match else path.stem.upper()),
        level=classify_level(line),
        message=line.strip()[:800],
        timestamp=ts_match.group(0) if ts_match else "",
        line_number=line_number,
    )


def scan_directory(path: str | Path, extensions: tuple[str, ...] = (".log", ".txt", ".out")) -> list[LogRecord]:
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Diretório de logs não encontrado: {root}")

    records: list[LogRecord] = []
    files = [item for item in sorted(root.rglob("*")) if item.is_file() and item.suffix.lower() in extensions]
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            if is_critical(line):
                records.append(parse_line(file_path, index, line))
    return records


def export_json(records: list[LogRecord], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_errors": len(records),
        "events": [asdict(item) for item in records],
    }
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest


def export_csv(records: list[LogRecord], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["timestamp", "host", "level", "source_file", "line_number", "message"]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in records:
            writer.writerow(asdict(item))
    return dest


def summarize(records: list[LogRecord]) -> dict:
    by_level: dict[str, int] = {}
    by_host: dict[str, int] = {}
    for item in records:
        by_level[item.level] = by_level.get(item.level, 0) + 1
        by_host[item.host] = by_host.get(item.host, 0) + 1
    return {
        "total": len(records),
        "by_level": by_level,
        "by_host": by_host,
        "top_messages": [item.message for item in records[:8]],
    }
