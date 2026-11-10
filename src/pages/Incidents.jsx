import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Incidents() {
  const [rows, setRows] = useState([]);
  const [evidence, setEvidence] = useState(null);
  const [current, setCurrent] = useState("");

  useEffect(() => {
    api("/api/incidents").then(setRows);
  }, []);

  async function correlate(code) {
    setCurrent(code);
    setEvidence(await api(`/api/incidents/${code}/correlate`, { method: "POST" }));
  }

  return (
    <div className="grid split">
      <div className="card">
        <h2>Incidentes reais da operação</h2>
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Título</th>
              <th>Host</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.code}</td>
                <td>
                  {item.title}
                  <div className="muted">
                    <span className={`badge ${item.severity}`}>{item.severity}</span> {item.support_level} · {item.status}
                  </div>
                </td>
                <td className="mono">{item.host}</td>
                <td>
                  <button className="ghost" onClick={() => correlate(item.code)}>
                    Correlacionar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Evidências {current && `· ${current}`}</h2>
        {!evidence && <p className="muted">Escolha um incidente para cruzar logs, chamados e runbooks.</p>}
        {evidence && (
          <>
            <p>
              Confiança <strong>{evidence.confidence}%</strong> · nível sugerido{" "}
              <span className="badge high">{evidence.suggested_level}</span>
            </p>
            <h3>Logs</h3>
            {evidence.related_logs.map((item) => (
              <p key={item.id} className="log-line">
                [{item.level}] {item.message}
              </p>
            ))}
            <h3>Chamados</h3>
            <ul>
              {evidence.related_tickets.map((item) => (
                <li key={item.id}>
                  {item.number} — {item.title}
                </li>
              ))}
            </ul>
            <h3>Base de conhecimento</h3>
            <ul>
              {evidence.suggested_kb.map((item) => (
                <li key={item.id}>
                  {item.code} · {item.title} ({item.level})
                </li>
              ))}
            </ul>
            <p className="notice">{evidence.next_action}</p>
          </>
        )}
      </div>
    </div>
  );
}
