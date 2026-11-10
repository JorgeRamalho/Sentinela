import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Automation() {
  const [catalog, setCatalog] = useState({ playbooks: [], simulate: true });
  const [jobs, setJobs] = useState([]);
  const [audit, setAudit] = useState({ audit: [], alerts: [] });
  const [action, setAction] = useState("clean_temp");
  const [target, setTarget] = useState("SRV-APP-02");
  const [message, setMessage] = useState("");

  async function load() {
    const [p, j, a] = await Promise.all([
      api("/api/automation/playbooks"),
      api("/api/automation/jobs"),
      api("/api/automation/audit"),
    ]);
    setCatalog(p);
    setJobs(j);
    setAudit(a);
  }

  useEffect(() => {
    load();
  }, []);

  async function run() {
    const result = await api("/api/automation/run", {
      method: "POST",
      body: JSON.stringify({ action, target, support_level: "N1", requested_by: "entrevista" }),
    });
    setMessage(`Job #${result.id} em modo ${result.mode}. Nada foi reiniciado de verdade.`);
    await load();
  }

  return (
    <div className="grid">
      <div className="notice">
        Trava dupla: <strong>SIMULATE=true</strong> e <strong>CONFIRM_EXECUTE=false</strong>. Telegram e Slack recebem o
        payload, mas só como simulação, com registro no audit trail.
      </div>
      <div className="grid split">
        <div className="card">
          <h2>Executar playbook</h2>
          <div className="actions">
            <select value={action} onChange={(event) => setAction(event.target.value)}>
              {catalog.playbooks.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.id} · {item.title} ({item.level})
                </option>
              ))}
            </select>
            <input value={target} onChange={(event) => setTarget(event.target.value)} />
            <button className="primary" onClick={run}>
              Executar em SIMULAR
            </button>
          </div>
          {message && <p className="notice">{message}</p>}
          <h3>Catálogo</h3>
          {catalog.playbooks.map((item) => (
            <p key={item.id}>
              <span className="mono">{item.id}</span> — {item.title} · risco {item.risk}
            </p>
          ))}
        </div>
        <div className="card">
          <h2>Alertas</h2>
          {audit.alerts.map((item) => (
            <p key={item.id}>
              <span className={`badge ${item.simulated ? "simulated" : "danger"}`}>{item.channel}</span> {item.title}
            </p>
          ))}
        </div>
      </div>
      <div className="card">
        <h2>Jobs e rastreabilidade</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Ação</th>
              <th>Alvo</th>
              <th>Modo</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.id}</td>
                <td>{item.action}</td>
                <td className="mono">{item.target}</td>
                <td>
                  <span className="badge simulated">{item.mode}</span>
                </td>
                <td>{item.result.note || item.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
