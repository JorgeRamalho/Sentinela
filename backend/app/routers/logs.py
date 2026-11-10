import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import LogEvent, LogScan
from app.services.log_collector import export_csv, export_json, scan_directory, summarize

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/scan")
def scan(db: Session = Depends(get_db)):
    settings = get_settings()
    try:
        records = scan_directory(settings.log_scan_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    export_dir = Path(settings.export_path)
    json_path = export_dir / f"erros-{stamp}.json"
    csv_path = export_dir / f"erros-{stamp}.csv"
    export_json(records, json_path)
    export_csv(records, csv_path)
    summary = summarize(records)

    scan_row = LogScan(
        files_scanned=len({item.source_file for item in records}) or 1,
        errors_found=len(records),
        output_json=str(json_path),
        output_csv=str(csv_path),
        summary=json.dumps(summary, ensure_ascii=False),
    )
    db.add(scan_row)
    db.flush()
    db.query(LogEvent).delete()
    for item in records:
        db.add(
            LogEvent(
                scan_id=scan_row.id,
                source_file=item.source_file,
                host=item.host,
                level=item.level,
                message=item.message,
                timestamp=item.timestamp,
                line_number=item.line_number,
            )
        )
    db.commit()
    db.refresh(scan_row)
    return {
        "scan_id": scan_row.id,
        "errors_found": scan_row.errors_found,
        "summary": summary,
        "output_json": scan_row.output_json,
        "output_csv": scan_row.output_csv,
    }


@router.get("/events")
def events(db: Session = Depends(get_db)):
    rows = db.query(LogEvent).order_by(LogEvent.id.desc()).limit(200).all()
    return [
        {
            "id": item.id,
            "source_file": item.source_file,
            "host": item.host,
            "level": item.level,
            "message": item.message,
            "timestamp": item.timestamp,
            "line_number": item.line_number,
        }
        for item in rows
    ]


@router.get("/export")
def export(fmt: str = "json"):
    settings = get_settings()
    folder = Path(settings.export_path)
    files = sorted(folder.glob(f"erros-*.{fmt}"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="Nenhuma exportação encontrada. Execute uma varredura primeiro.")
    media = "application/json" if fmt == "json" else "text/csv"
    return FileResponse(files[0], media_type=media, filename=files[0].name)
