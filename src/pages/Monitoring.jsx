import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Monitoring() {
  const [metrics, setMetrics] = useState([]);
  const [services, setServices] = useState([]);

  async function load() {
    const [m, s] = await Promise.all([api("/api/monitoring/metrics"), api("/api/monitoring/services")]);
    setMetrics(m.hosts);
    setServices(s.services);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  return (
    <div className="grid">
      <div className="actions">
        <button className="primary" onClick={load}>
          Recoletar métricas
        </button>
        <span className="muted">LOCAL-CONSOLE usa psutil de verdade. Os demais hosts são a fazenda de sustentação da demo.</span>
      </div>
      <div className="grid cards-3">
        {metrics.map((host) => {
          const worst = Math.max(host.cpu_percent, host.memory_percent, host.disk_percent);
          const cls = worst >= 95 ? "danger" : worst >= 88 ? "warn" : "";
          return (
            <div className="card" key={host.host}>
              <h3>{host.host}</h3>
              <p className="muted">
                {host.role} · {host.real ? "coleta real" : "baseline simulada"}
              </p>
              <p>
                CPU {host.cpu_percent}% · MEM {host.memory_percent}% · DISK {host.disk_percent}%
              </p>
              <div className={`bar ${cls}`}>
                <span style={{ width: `${Math.min(worst, 100)}%` }} />
              </div>
              {host.suggestions?.length > 0 && (
                <p className="muted">Sugerido: {host.suggestions.map((item) => item.action).join(", ")}</p>
              )}
            </div>
          );
        })}
      </div>
      <div className="card">
        <h2>Serviços</h2>
        <table>
          <thead>
            <tr>
              <th>Serviço</th>
              <th>Host</th>
              <th>PID</th>
              <th>Status</th>
              <th>Observação</th>
            </tr>
          </thead>
          <tbody>
            {services.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td className="mono">{item.host}</td>
                <td className="mono">{item.pid}</td>
                <td>
                  <span className={`badge ${item.status}`}>{item.status}</span>
                </td>
                <td>{item.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
