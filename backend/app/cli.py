"""CLI Sentinela — as mesmas rotinas da API, para demonstrar no terminal da entrevista."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.seed import seed_if_empty
from app.services.automation_engine import run_action
from app.services.log_collector import export_csv, export_json, scan_directory, summarize
from app.services.ticket_reports import weekly_report


def _session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_if_empty(db)
    return db


def cmd_logs(args: argparse.Namespace) -> None:
    settings = get_settings()
    path = args.path or settings.log_scan_path
    records = scan_directory(path)
    summary = summarize(records)
    export_dir = Path(args.out or settings.export_path)
    json_file = export_json(records, export_dir / "erros-cli.json")
    csv_file = export_csv(records, export_dir / "erros-cli.csv")
    print(json.dumps({"summary": summary, "json": str(json_file), "csv": str(csv_file)}, ensure_ascii=False, indent=2))


def cmd_automate(args: argparse.Namespace) -> None:
    db = _session()
    try:
        job = run_action(db, args.action, args.target, args.level, "cli")
        print(json.dumps({"id": job.id, "status": job.status, "mode": job.mode, "result": job.result}, ensure_ascii=False, indent=2))
    finally:
        db.close()


def cmd_report(_: argparse.Namespace) -> None:
    db = _session()
    try:
        payload = weekly_report(db)
        print(json.dumps({k: payload[k] for k in ("period", "metrics", "open_priority", "subject")}, ensure_ascii=False, indent=2))
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sentinela CLI — sustentação N1/N2")
    sub = parser.add_subparsers(dest="command", required=True)

    logs = sub.add_parser("logs", help="Varrer logs e exportar CSV/JSON apenas com erros críticos")
    logs.add_argument("--path", default=None)
    logs.add_argument("--out", default=None)
    logs.set_defaults(func=cmd_logs)

    auto = sub.add_parser("automate", help="Executar playbook N1/N2 (SIMULAR por padrão)")
    auto.add_argument("--action", required=True, choices=["clean_temp", "restart_service", "recycle_app_pool", "clear_cache", "analyze_db_locks"])
    auto.add_argument("--target", required=True)
    auto.add_argument("--level", default="N1")
    auto.set_defaults(func=cmd_automate)

    report = sub.add_parser("report", help="Gerar relatório semanal de SLA")
    report.set_defaults(func=cmd_report)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
