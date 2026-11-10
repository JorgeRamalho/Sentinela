from app.database import Base, SessionLocal, engine
from app.seed import seed_if_empty
from app.services.automation_engine import PLAYBOOKS, evaluate_thresholds, run_action


def test_thresholds_suggest_n1_playbooks():
    suggestions = evaluate_thresholds(disk_percent=96, memory_percent=93, service_down=True)
    actions = {item["action"] for item in suggestions}
    assert "clean_temp" in actions
    assert "recycle_app_pool" in actions
    assert "restart_service" in actions


def test_run_action_stays_in_simulate_mode():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        job = run_action(db, "clean_temp", "SRV-APP-02")
        assert job.mode == "simulate"
        assert job.status == "simulated"
        assert "Nenhum processo foi reiniciado" in job.result
        assert "clean_temp" in PLAYBOOKS
    finally:
        db.close()
