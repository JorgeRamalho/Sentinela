import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [sla, setSla] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    Promise.all([api("/api/tickets"), api("/api/tickets/sla")]).then(([rows, metrics]) => {
      setTickets(rows);
      setSla(metrics);
    });
  }, []);

  async function sendReport() {
    setReport(await api("/api/tickets/report", { method: "POST" }));
  }

  return (
    <div className="grid">
      {sla && (
        <div className="grid kpis">
          <div className="card">
            <h3>Abertos vs fechados</h3>
            <p className="metric">{sla.open} / {sla.closed}</p>
            <p className="muted">Total {sla.total} · fontes {Object.keys(sla.by_source).join(", ")}</p>
          </div>
          <div className="card">
            <h3>Tempo médio de atendimento</h3>
            <p className="metric">{sla.avg_resolution_minutes} min</p>
            <p className="muted">1ª resposta {sla.avg_first_response_minutes} min</p>
          </div>
          <div className="card">
            <h3>Compliance SLA</h3>
            <p className="metric">{sla.sla_compliance_percent}%</p>
            <p className="muted">{sla.sla_breaches} violações na janela</p>
          </div>
          <div className="card">
            <h3>Relatório semanal</h3>
            <p className="muted">Compilado HTML enviado por e-mail em modo SIMULAR.</p>
            <button className="primary" onClick={sendReport}>
              Gerar e enviar
            </button>
          </div>
        </div>
      )}
      {report && (
        <div className="card">
          <h2>{report.subject}</h2>
          <div dangerouslySetInnerHTML={{ __html: report.email_html }} />
        </div>
      )}
      <div className="card">
        <h2>Chamados</h2>
        <table>
          <thead>
            <tr>
              <th>Número</th>
              <th>Título</th>
              <th>Fonte</th>
              <th>Prioridade</th>
              <th>Status</th>
              <th>SLA</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.number}</td>
                <td>
                  {item.title}
                  <div className="muted">
                    {item.requester} · {item.assignee}
                  </div>
                </td>
                <td>{item.source}</td>
                <td>
                  <span className={`badge ${item.priority}`}>{item.priority}</span>
                </td>
                <td>
                  <span className={`badge ${item.status}`}>{item.status}</span>
                </td>
                <td className="mono">{item.sla_minutes}m</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
