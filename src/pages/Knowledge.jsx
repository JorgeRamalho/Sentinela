import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Knowledge() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState([]);

  async function search(term = q) {
    const query = term ? `?q=${encodeURIComponent(term)}` : "";
    setRows(await api(`/api/knowledge${query}`));
  }

  useEffect(() => {
    search("");
  }, []);

  return (
    <div className="grid">
      <div className="card">
        <h2>Runbooks N1 / N2</h2>
        <div className="actions">
          <input
            placeholder="disco, oracle, iis, totvs, ssl..."
            value={q}
            onChange={(event) => setQ(event.target.value)}
            onKeyDown={(event) => event.key === "Enter" && search()}
          />
          <button className="primary" onClick={() => search()}>
            Buscar
          </button>
        </div>
      </div>
      <div className="kb">
        {rows.map((item) => (
          <article key={item.id}>
            <p className="kicker">
              {item.code} · {item.support_level} · {item.category}
            </p>
            <h3>{item.title}</h3>
            <p>
              <strong>Sintomas.</strong> {item.symptoms}
            </p>
            <p>
              <strong>Diagnóstico.</strong> {item.diagnosis}
            </p>
            <pre>{item.resolution}</pre>
          </article>
        ))}
      </div>
    </div>
  );
}
