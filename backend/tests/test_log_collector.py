from pathlib import Path

from app.services.log_collector import is_critical, scan_directory, summarize


def test_filters_only_critical_lines():
    assert is_critical("2026 ERROR disk full")
    assert is_critical("FATAL listener down")
    assert is_critical("NullPointerException in billing")
    assert is_critical("ORA-00020: maximum number of processes")
    assert not is_critical("INFO GET /health 200")
    assert not is_critical("WARN latência 2.4s")


def test_scan_sample_logs():
    root = Path(__file__).resolve().parents[2] / "data" / "logs"
    records = scan_directory(root)
    assert len(records) >= 10
    levels = {item.level for item in records}
    assert "ERROR" in levels or "FATAL" in levels or "Exception" in levels
    summary = summarize(records)
    assert summary["total"] == len(records)
    assert summary["by_host"]
