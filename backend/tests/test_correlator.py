from app.models import Incident, KnowledgeArticle, LogEvent, Ticket
from app.services.correlator import correlate


def test_oracle_incident_suggests_n2_and_kb():
    incident = Incident(
        code="INC-1043",
        title="Oracle atingiu o limite de processos",
        description="ORA-00020 no ORCL-FIN",
        host="SRV-DB-ORACLE",
        support_level="N1",
        source="alert-oracle",
    )
    logs = [
        LogEvent(source_file="db-oracle.log", host="SRV-DB-ORACLE", level="ERROR", message="ORA-00020: maximum number of processes", timestamp="", line_number=3)
    ]
    tickets = [Ticket(number="JIRA-SD-1022", title="ORA-00020: maximum number of processes exceeded", requester="x")]
    articles = [
        KnowledgeArticle(code="KB-002", title="ORA-00020 maximum processes", category="banco", symptoms="ORA-00020", diagnosis="", resolution="", tags="oracle,ora-00020,n2", support_level="N2")
    ]
    result = correlate(incident, logs, tickets, articles)
    assert result["suggested_level"] == "N2"
    assert result["related_logs"]
    assert result["suggested_kb"][0]["code"] == "KB-002"
    assert result["confidence"] >= 50
