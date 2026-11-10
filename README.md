# Sentinela — plataforma de sustentação N1 / N2

Console operacional para apresentar em entrevista técnica: monitoramento, identificação de incidentes, correlação de evidências, automação controlada, chamados com SLA e base de conhecimento.

O objetivo não é “reiniciar serviço de qualquer jeito”. É mostrar como um time de sustentação **identifica**, **diagnostica**, **executa com trava de segurança** e **deixa rastro**.

## O que você demonstra

| Módulo | O que faz |
| --- | --- |
| Dashboard | KPIs de incidentes, fila, SLA e hosts |
| Monitoramento | CPU/memória/disco (psutil no console local + fazenda de servidores) |
| Incidentes | Incidentes reais da demo + correlação com logs, chamados e runbooks |
| Chamados | GLPI / Jira / ServiceNow / Zendesk, TMA e relatório semanal por e-mail (simulado) |
| Analisador de logs | Varre `data/logs`, filtra ERROR/FATAL/Exception e exporta CSV/JSON |
| Automação N1/N2 | Limpeza de temp, recycle IIS, restart, locks de banco — **SIMULAR=true** |
| Banco de dados | Saúde de Oracle, SQL Server, PostgreSQL e Redis sustentados |
| Fornecedores | Contrato, SLA e a quem escalar |
| Base de conhecimento | Runbooks N1/N2 pesquisáveis |

`index.html` fica na **raiz do projeto** (entrada Vite/React), como pedido.

## Arquitetura

```
React (index.html + src/)  →  FastAPI /api  →  SQLite + serviços Python
                                      ↓
                       Jenkinsfile  |  docker-compose (api, web, jenkins)
```

Decisões que valem na entrevista:

1. **SIMULATE=true por padrão.** Nenhuma pasta é apagada e nenhum serviço é reiniciado. O job descreve o que *seria* feito e grava audit trail.
2. **CONFIRM_EXECUTE** é a segunda trava. Só existiria em janela de mudança.
3. **Alertas Telegram/Slack** nascem no mesmo fluxo, também simulados se não houver token.
4. **Coletor de logs** é determinístico e testável: regex de ERROR/FATAL/Exception/ORA-*.
5. **Correlação** cruza incidente × logs × chamado × KB e sugere N1 ou N2.
6. **Jenkins em Docker** executa o mesmo pipeline que `scripts/ci-local.ps1`.

## Subir para a entrevista (Windows)

```powershell
cd "j:\area de trabalho\Fron_End\Projetos\Projeto-Sentinela"
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Terminal 1 — API:

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — console:

```powershell
npm install
npm run dev
```

Abra [http://127.0.0.1:5173](http://127.0.0.1:5173). API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Atalho: `.\scripts\start-demo.ps1`

## CLI (bom de mostrar no terminal)

```powershell
cd backend
python -m app.cli logs
python -m app.cli automate --action clean_temp --target SRV-APP-02
python -m app.cli report
```

## Testes e pipeline

```powershell
cd backend
python -m pytest -q
```

CI local (os mesmos estágios do `Jenkinsfile`):

```powershell
.\scripts\ci-local.ps1
```

Stack completa:

```powershell
docker compose up --build
```

- App: http://localhost
- API: http://localhost:8000
- Jenkins: http://localhost:8080

## Roteiro de 5 minutos na entrevista

1. Dashboard: “estes são os incidentes que o NOC veria hoje”.
2. Analisador de logs: varrer → só erro crítico → baixar CSV.
3. INC-1043 (Oracle): correlacionar → KB-002 → nível N2 e fornecedor Oracle.
4. Automação: `clean_temp` em SRV-APP-02 → job `simulated` + alerta Telegram/Slack.
5. Chamados: gerar relatório semanal de SLA.
6. Jenkinsfile: lint/testes, build React, *safety gate* que bloqueia se `SIMULATE` não for true.

## Estrutura

```
index.html              ← raiz, obrigatório
src/                    React (9 módulos)
backend/app/            FastAPI, modelos, serviços, CLI
backend/tests/          pytest
data/logs               evidências da demo
Jenkinsfile             CI/CD
docker-compose.yml      api + web + jenkins
```
