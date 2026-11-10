import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function LogAnalyzer() {
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [busy, setBusy] = useState(false);

  async function loadEvents() {
    setEvents(await api("/api/logs/events"));
  }

  useEffect(() => {
    loadEvents().catch(() => undefined);
  }, []);

  async function scan() {
    setBusy(true);
    try {
      const result = await api("/api/logs/scan", { method: "POST" });
      setSummary(result);
      await loadEvents();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid">
      <div className="card">
        <h2>Coletor e limpador de logs</h2>
        <p className="muted">
          Varre <span className="mono">data/logs</span> e mantém só ERROR, FATAL, CRITICAL, Exception e ORA-*.
        </p>
        <div className="actions">
          <button className="primary" disabled={busy} onClick={scan}>
            {busy ? "Varrendo..." : "Varrer logs agora"}
          </button>
          <a className="btn" href="/api/logs/export?fmt=json">
            Baixar JSON
          </a>
          <a className="btn" href="/api/logs/export?fmt=csv">
            Baixar CSV
          </a>
        </div>
        {summary && (
          <p className="notice">
            {summary.errors_found} erros extraídos · JSON {summary.output_json}
          </p>
        )}
      </div>
      <div className="card">
        <h2>Resumo limpo</h2>
        <table>
          <thead>
            <tr>
              <th>Quando</th>
              <th>Host</th>
              <th>Nível</th>
              <th>Arquivo</th>
              <th>Mensagem</th>
            </tr>
          </thead>
          <tbody>
            {events.map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.timestamp}</td>
                <td className="mono">{item.host}</td>
                <td>
                  <span className={`badge ${item.level === "INFO" ? "ok" : "critical"}`}>{item.level}</span>
                </td>
                <td className="mono">{item.source_file}:{item.line_number}</td>
                <td>{item.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
