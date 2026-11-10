import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/dashboard/summary")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <p className="notice">Não foi possível falar com a API: {error}</p>;
  }
  if (!data) {
    return <p className="muted">Carregando console...</p>;
  }

  const sla = data.kpis.sla;
  const chart = [
    { name: "Abertos", value: sla.open },
    { name: "Fechados", value: sla.closed },
    { name: "Breach", value: sla.sla_breaches },
  ];

  return (
    <div className="grid">
      <div className="grid kpis">
        <div className="card">
          <h3>Incidentes abertos</h3>
          <p className="metric">{data.kpis.open_incidents}</p>
          <p className="muted">{data.kpis.critical_incidents} críticos · correlação pronta</p>
        </div>
        <div className="card">
          <h3>Chamados na fila</h3>
          <p className="metric">{data.kpis.open_tickets}</p>
          <p className="muted">GLPI · Jira · ServiceNow · Zendesk</p>
        </div>
        <div className="card">
          <h3>SLA semanal</h3>
          <p className="metric">{sla.sla_compliance_percent}%</p>
          <p className="muted">TMA {sla.avg_resolution_minutes} min · 1ª resposta {sla.avg_first_response_minutes} min</p>
        </div>
        <div className="card">
          <h3>Bancos degradados</h3>
          <p className="metric">{data.kpis.databases_degraded}</p>
          <p className="muted">Oracle ORCL-FIN no limite de sessões</p>
        </div>
      </div>

      <div className="grid split">
        <div className="card">
          <h2>Fila de prioridade</h2>
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Incidente</th>
                <th>Host</th>
                <th>Nível</th>
              </tr>
            </thead>
            <tbody>
              {data.priority_incidents.map((item) => (
                <tr key={item.code}>
                  <td className="mono">{item.code}</td>
                  <td>
                    {item.title}
                    <div className="muted">{item.status}</div>
                  </td>
                  <td className="mono">{item.host}</td>
                  <td>
                    <span className={`badge ${item.severity}`}>{item.level}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <Link className="btn" to="/incidentes">
              Correlacionar evidências
            </Link>
          </p>
        </div>
        <div className="card">
          <h2>Chamados da semana</h2>
          <div style={{ height: 220 }}>
            <ResponsiveContainer>
              <BarChart data={chart}>
                <XAxis dataKey="name" stroke="#8aa399" />
                <YAxis stroke="#8aa399" />
                <Tooltip />
                <Bar dataKey="value" fill="#2ee6a6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid split">
        <div className="card">
          <h2>Fazenda monitorada</h2>
          <table>
            <thead>
              <tr>
                <th>Host</th>
                <th>CPU</th>
                <th>Mem</th>
                <th>Disco</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.hosts.map((host) => (
                <tr key={host.host}>
                  <td className="mono">{host.host}</td>
                  <td>{host.cpu_percent}%</td>
                  <td>{host.memory_percent}%</td>
                  <td>{host.disk_percent}%</td>
                  <td>
                    <span className={`badge ${host.status}`}>{host.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card">
          <h2>Últimas automações</h2>
          {data.recent_jobs.length === 0 && (
            <p className="muted">Nenhum playbook executado ainda. Use Automação N1/N2 em modo SIMULAR.</p>
          )}
          {data.recent_jobs.map((job) => (
            <p key={job.id}>
              <span className="mono">{job.action}</span> → {job.target}{" "}
              <span className={`badge ${job.status}`}>{job.mode}</span>
            </p>
          ))}
          <p className="muted">Alertas Telegram/Slack também nascem simulados e entram no audit trail.</p>
        </div>
      </div>
    </div>
  );
}
