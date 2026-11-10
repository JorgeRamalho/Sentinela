def test_health_and_dashboard(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["simulate"] is True
    dash = client.get("/api/dashboard/summary")
    assert dash.status_code == 200
    body = dash.json()
    assert body["kpis"]["open_incidents"] >= 1
    assert body["kpis"]["sla"]["total"] >= 1


def test_log_scan_and_automation_and_report(client):
    scanned = client.post("/api/logs/scan")
    assert scanned.status_code == 200
    assert scanned.json()["errors_found"] >= 10

    run = client.post(
        "/api/automation/run",
        json={"action": "restart_service", "target": "IIS", "support_level": "N1"},
    )
    assert run.status_code == 200
    assert run.json()["mode"] == "simulate"

    report = client.post("/api/tickets/report")
    assert report.status_code == 200
    assert "sla_compliance_percent" in report.json()["metrics"]

    correlated = client.post("/api/incidents/INC-1042/correlate")
    assert correlated.status_code == 200
    assert "confidence" in correlated.json()
