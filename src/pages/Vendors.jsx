import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Vendors() {
  const [rows, setRows] = useState([]);
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    api("/api/vendors").then(setRows);
  }, []);

  return (
    <div className="grid split">
      <div className="card">
        <h2>Contratos e fila de fornecedor</h2>
        <table>
          <thead>
            <tr>
              <th>Fornecedor</th>
              <th>Categoria</th>
              <th>SLA</th>
              <th>Contrato</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.category}</td>
                <td>{item.sla_hours}h</td>
                <td className="mono">{item.contract_until}</td>
                <td>
                  <button className="ghost" onClick={() => api(`/api/vendors/${item.id}`).then(setDetail)}>
                    Abrir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Escalonamento</h2>
        {!detail && <p className="muted">Selecione um fornecedor para ver bases e runbooks ligados ao contrato.</p>}
        {detail?.vendor && (
          <>
            <h3>{detail.vendor.name}</h3>
            <p>{detail.vendor.notes}</p>
            <p className="muted">{detail.vendor.contact}</p>
            <h3>Instâncias</h3>
            <ul>
              {detail.databases.map((item) => (
                <li key={item.name}>
                  {item.name} · {item.status}
                </li>
              ))}
            </ul>
            <h3>Artigos</h3>
            <ul>
              {detail.articles.map((item) => (
                <li key={item.code}>
                  {item.code} · {item.title} ({item.level})
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
