from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    DatabaseInstance,
    Incident,
    KnowledgeArticle,
    MonitoredService,
    Ticket,
    Vendor,
)


def seed_if_empty(db: Session) -> None:
    if db.query(Vendor).count():
        return

    now = datetime.now(timezone.utc)
    vendors = [
        Vendor(name="Microsoft", category="plataforma", contact="css@microsoft.com", sla_hours=4, contract_until="2027-12-31", notes="IIS, Windows Server, SQL Server, Azure."),
        Vendor(name="Oracle", category="banco", contact="support@oracle.com", sla_hours=2, contract_until="2026-09-30", notes="Oracle Database 19c financeiro."),
        Vendor(name="TOTVS", category="erp", contact="suporte@totvs.com.br", sla_hours=4, contract_until="2026-06-30", notes="Protheus / integração API."),
        Vendor(name="AWS", category="nuvem", contact="aws-enterprise@amazon.com", sla_hours=1, contract_until="2027-03-31", notes="EC2, RDS, S3 backup."),
        Vendor(name="Cisco", category="rede", contact="tac@cisco.com", sla_hours=4, contract_until="2026-11-30", notes="VPN, firewall, switches core."),
        Vendor(name="Glpi MSP Local", category="service-desk", contact="n2@msp.local", sla_hours=8, contract_until="2026-12-31", notes="Fila de campo e plantão."),
    ]
    db.add_all(vendors)
    db.flush()
    by_name = {item.name: item for item in vendors}

    db.add_all(
        [
            DatabaseInstance(name="ORCL-FIN", engine="Oracle 19c", host="SRV-DB-ORACLE", port=1521, status="degraded", connections=198, max_connections=200, latency_ms=420, vendor_id=by_name["Oracle"].id, role="prod"),
            DatabaseInstance(name="SQL-RH", engine="SQL Server 2019", host="SRV-SQL-RH", port=1433, status="healthy", connections=42, max_connections=120, latency_ms=18, vendor_id=by_name["Microsoft"].id, role="prod"),
            DatabaseInstance(name="PG-ERP", engine="PostgreSQL 16", host="SRV-PG-01", port=5432, status="healthy", connections=67, max_connections=150, latency_ms=11, vendor_id=by_name["AWS"].id, role="prod"),
            DatabaseInstance(name="REDIS-CACHE", engine="Redis 7", host="SRV-APP-01", port=6379, status="healthy", connections=210, max_connections=1000, latency_ms=2, vendor_id=by_name["AWS"].id, role="cache"),
        ]
    )

    tickets = [
        Ticket(number="GLPI-88421", title="Disco C: em 96% no SRV-APP-02", requester="NOC", priority="critical", status="in_progress", source="glpi", sla_minutes=60, first_response_minutes=8, assignee="ana.n1", opened_at=now - timedelta(hours=3)),
        Ticket(number="GLPI-88418", title="Lentidão no login LDAP", requester="RH", priority="high", status="in_progress", source="glpi", sla_minutes=240, first_response_minutes=22, assignee="bruno.n1", opened_at=now - timedelta(hours=6)),
        Ticket(number="JIRA-SD-1022", title="ORA-00020: maximum number of processes exceeded", requester="Financeiro", priority="critical", status="open", source="jira", sla_minutes=60, first_response_minutes=5, assignee="carla.n2", opened_at=now - timedelta(hours=2)),
        Ticket(number="SNOW-INC001089", title="w3wp.exe consumo de memória no IIS", requester="Portal", priority="high", status="pending", source="servicenow", sla_minutes=240, first_response_minutes=15, assignee="ana.n1", opened_at=now - timedelta(hours=10)),
        Ticket(number="ZD-44190", title="Timeout integração TOTVS Protheus", requester="Faturamento", priority="high", status="open", source="zendesk", sla_minutes=240, first_response_minutes=40, assignee="diego.n2", opened_at=now - timedelta(hours=8)),
        Ticket(number="GLPI-88390", title="Certificado SSL portal.empresa.local expira em 9 dias", requester="Segurança", priority="medium", status="open", source="glpi", sla_minutes=480, first_response_minutes=50, assignee="fila-n1", opened_at=now - timedelta(days=2)),
        Ticket(number="GLPI-88310", title="Job de backup noturno falhou no SRV-FILE-01", requester="Infra", priority="high", status="resolved", source="glpi", sla_minutes=240, first_response_minutes=12, resolution_minutes=110, assignee="bruno.n1", opened_at=now - timedelta(days=3), closed_at=now - timedelta(days=3, hours=-2)),
        Ticket(number="JIRA-SD-1001", title="Reset de senha VPN (lote RH)", requester="RH", priority="low", status="closed", source="jira", sla_minutes=480, first_response_minutes=6, resolution_minutes=25, assignee="ana.n1", opened_at=now - timedelta(days=4), closed_at=now - timedelta(days=4, hours=-1)),
        Ticket(number="GLPI-88200", title="Impressora do 4º andar offline", requester="Facilities", priority="low", status="closed", source="glpi", sla_minutes=480, first_response_minutes=30, resolution_minutes=90, assignee="fila-n1", opened_at=now - timedelta(days=5), closed_at=now - timedelta(days=5, hours=-3)),
        Ticket(number="SNOW-INC001012", title="Exception NullPointer no módulo de faturamento", requester="TI Apps", priority="high", status="resolved", source="servicenow", sla_minutes=240, first_response_minutes=18, resolution_minutes=300, assignee="diego.n2", opened_at=now - timedelta(days=2), closed_at=now - timedelta(days=1, hours=20)),
        Ticket(number="GLPI-88400", title="Recycle preventivo do pool ERP-WEB", requester="N1", priority="medium", status="closed", source="glpi", sla_minutes=240, first_response_minutes=4, resolution_minutes=15, assignee="ana.n1", opened_at=now - timedelta(days=1), closed_at=now - timedelta(hours=20)),
        Ticket(number="ZD-44002", title="Acesso liberado ao share \\\\files\\contabil", requester="Contábil", priority="low", status="closed", source="zendesk", sla_minutes=480, first_response_minutes=20, resolution_minutes=45, assignee="bruno.n1", opened_at=now - timedelta(days=6), closed_at=now - timedelta(days=6, hours=-2)),
    ]
    db.add_all(tickets)
    db.flush()
    ticket_by_number = {item.number: item for item in tickets}

    db.add_all(
        [
            Incident(code="INC-1042", title="Disco crítico em SRV-APP-02", description="Volume C: em 96%. Risco de parada do IIS e falha de escrita de logs.", severity="critical", status="investigating", source="monitor-disco", host="SRV-APP-02", support_level="N1", ticket_id=ticket_by_number["GLPI-88421"].id, evidence='{"disk":96.1,"mount":"C:"}'),
            Incident(code="INC-1043", title="Oracle atingiu o limite de processos", description="ORA-00020 no ORCL-FIN. Sessões zumbis suspeitas após lote noturno.", severity="critical", status="open", source="alert-oracle", host="SRV-DB-ORACLE", support_level="N2", ticket_id=ticket_by_number["JIRA-SD-1022"].id, evidence='{"ora":"00020","sessions":198}'),
            Incident(code="INC-1044", title="Memory leak no w3wp do portal", description="Application pool ERP-WEB acima de 93% de memória. Recycle N1 pendente de janela.", severity="high", status="investigating", source="monitor-memoria", host="SRV-WEB-01", support_level="N1", ticket_id=ticket_by_number["SNOW-INC001089"].id, evidence='{"process":"w3wp","memory":93.4}'),
            Incident(code="INC-1045", title="Timeout na API TOTVS", description="Faturamento com HTTP 504 ao consultar Protheus. Possível lock no banco ou saturação do pool.", severity="high", status="open", source="apm", host="SRV-APP-01", support_level="N2", ticket_id=ticket_by_number["ZD-44190"].id, evidence='{"endpoint":"/protheus/orders","latency_ms":15000}'),
            Incident(code="INC-1046", title="Certificado SSL próximo do vencimento", description="portal.empresa.local expira em 9 dias. Risco de quebra de HTTPS para usuários externos.", severity="medium", status="open", source="scanner-cert", host="SRV-WEB-01", support_level="N1", ticket_id=ticket_by_number["GLPI-88390"].id, evidence='{"days_left":9,"cn":"portal.empresa.local"}'),
            Incident(code="INC-1047", title="Backup noturno inconsistente", description="Job Veeam no SRV-FILE-01 falhou por espaço. Restauração pontual em risco.", severity="high", status="mitigated", source="backup-job", host="SRV-FILE-01", support_level="N1", ticket_id=ticket_by_number["GLPI-88310"].id, evidence='{"job":"VEEAM-NIGHTLY","code":"NO_SPACE"}', resolved_at=now - timedelta(days=2)),
            Incident(code="INC-1048", title="NullPointerException no faturamento", description="Exception recorrente no módulo billing após deploy. Correlação com logs de aplicação.", severity="high", status="resolved", source="log-collector", host="SRV-APP-01", support_level="N2", ticket_id=ticket_by_number["SNOW-INC001012"].id, evidence='{"exception":"NullPointerException","module":"billing"}', resolved_at=now - timedelta(days=1)),
        ]
    )

    db.add_all(
        [
            MonitoredService(name="IIS / W3SVC", host="SRV-WEB-01", status="degraded", pid="4480", message="w3wp com memória elevada"),
            MonitoredService(name="Oracle TNS Listener", host="SRV-DB-ORACLE", status="up", pid="1124", message="Listener ok; sessões no limite"),
            MonitoredService(name="App Faturamento", host="SRV-APP-01", status="up", pid="2201", message="Latência da API TOTVS alta"),
            MonitoredService(name="LDAP / AD DS", host="DC-01", status="up", pid="512", message="Timeouts intermitentes às 08h"),
            MonitoredService(name="Jenkins CI", host="LOCAL-CONSOLE", status="up", pid="docker", message="Pipeline Jenkinsfile pronta"),
            MonitoredService(name="Redis Cache", host="SRV-APP-01", status="up", pid="6379", message="Hit ratio 94%"),
        ]
    )

    db.add_all(
        [
            KnowledgeArticle(code="KB-001", title="Disco cheio em servidor Windows / IIS", category="sistema", support_level="N1", tags="disco,temp,iis,n1", vendor_id=by_name["Microsoft"].id, symptoms="Alertas de disco >90%, sites IIS fora, falha ao gravar log.", diagnosis="Identificar pastas Temp, logs IIS e dumps. Confirmar que não há crescimento de banco em disco de SO.", resolution="1) Registrar chamado e evidência.\n2) Em SIMULAR, executar playbook clean_temp.\n3) Validar % livre.\n4) Se logs de aplicação cresceram, rotacionar.\n5) Escalar a N2 se o volume for de dados."),
            KnowledgeArticle(code="KB-002", title="ORA-00020 maximum processes", category="banco", support_level="N2", tags="oracle,ora-00020,sessoes,n2", vendor_id=by_name["Oracle"].id, symptoms="Aplicações financeiras recusam conexão. Alert log com ORA-00020.", diagnosis="Verificar v$session, processos zumbis, jobs noturnos e processes/sessions no pfile.", resolution="1) Não reiniciar o banco sem janela.\n2) Coletar evidência (sessões inativas).\n3) Playbook analyze_db_locks em modo SIMULAR.\n4) Abrir chamado no fornecedor Oracle se processes precisar aumentar."),
            KnowledgeArticle(code="KB-003", title="Recycle de Application Pool IIS", category="aplicacao", support_level="N1", tags="iis,w3wp,memoria,recycle,n1", vendor_id=by_name["Microsoft"].id, symptoms="w3wp crescendo, portal lento, HTTP 503 intermitente.", diagnosis="Confirmar pool, correlacionar com deploy recente e dumps de memória.", resolution="1) Comunicar usuários-chave.\n2) Executar recycle_app_pool em SIMULAR.\n3) Acompanhar memória 15 min.\n4) Se recidivar, escalar N2 com dump."),
            KnowledgeArticle(code="KB-004", title="Timeout de integração TOTVS Protheus", category="integracao", support_level="N2", tags="totvs,timeout,api,n2", vendor_id=by_name["TOTVS"].id, symptoms="HTTP 504, faturamento parado, fila de pedidos.", diagnosis="Checar disponibilidade do AppServer, locks no banco e certificado do endpoint.", resolution="1) Validar saúde do Protheus e do banco PG-ERP.\n2) Correlacionar logs da API.\n3) Acionar fornecedor TOTVS se for lock interno do ERP."),
            KnowledgeArticle(code="KB-005", title="Renovação de certificado SSL", category="seguranca", support_level="N1", tags="ssl,certificado,https,n1", vendor_id=by_name["Microsoft"].id, symptoms="Alerta de expiração, aviso no navegador, integrações quebrando.", diagnosis="Listar bind do IIS / nginx, cadeia intermediária e SAN.", resolution="1) Solicitar emissão ao time de segurança.\n2) Agendar janela.\n3) Atualizar bind e validar TLS."),
            KnowledgeArticle(code="KB-006", title="Falha de backup por espaço em disco", category="backup", support_level="N1", tags="backup,disco,veeam,n1", vendor_id=by_name["AWS"].id, symptoms="Job nightly failed, NO_SPACE, retenção atrasada.", diagnosis="Checar repositório, snapshots órfãos e crescimento do volume de arquivos.", resolution="1) Liberar retenção expirada.\n2) Reexecutar job em janela.\n3) Abrir capacidade com storage."),
            KnowledgeArticle(code="KB-007", title="NullPointerException após deploy", category="aplicacao", support_level="N2", tags="exception,deploy,java,n2", symptoms="Stacktrace em log, 500 no módulo billing.", diagnosis="Isolar release, feature flag e dados nulos em payload.", resolution="1) Coletar stacktrace via analisador de logs.\n2) Rollback se houver feature flag.\n3) Abrir defeito para o time de aplicação."),
            KnowledgeArticle(code="KB-008", title="Timeout LDAP / autenticação", category="rede", support_level="N1", tags="ldap,ad,login,n1", vendor_id=by_name["Microsoft"].id, symptoms="Usuários sem logon, timeout 389/636.", diagnosis="Testar DC, DNS e latência. Evitar restart do AD sem N2.", resolution="1) Testar nltest / dcdiag (somente leitura).\n2) Failover de DC se documentado.\n3) Escalar Cisco/Microsoft se for WAN."),
            KnowledgeArticle(code="KB-009", title="Quando escalar de N1 para N2", category="processo", support_level="N1", tags="escalonamento,n1,n2,processo", symptoms="Playbook N1 não restabelece o serviço em 30 min ou há risco de dados.", diagnosis="Severidade crítica + evidência insuficiente no nível 1.", resolution="1) Anexar logs filtrados.\n2) Registrar automação SIMULADA já tentada.\n3) Acionar N2 e fornecedor se houver contrato."),
            KnowledgeArticle(code="KB-010", title="Uso seguro da automação Sentinela", category="processo", support_level="N1", tags="automacao,simular,change,n1", symptoms="Operador precisa limpar cache ou reiniciar serviço.", diagnosis="Confirmar SIMULATE=true fora da janela de mudança.", resolution="1) Rodar em SIMULAR.\n2) Anexar o job no chamado.\n3) Só promover CONFIRM_EXECUTE com CAB/change aberta."),
        ]
    )
    db.commit()
