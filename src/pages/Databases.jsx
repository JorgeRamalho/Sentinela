import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Databases() {
  const [health, setHealth] = useState([]);

  useEffect(() => {
    api("/api/databases/health").then((body) => setHealth(body.instances));
  }, []);

  return (
    <div className="grid">
      <p className="muted">
        Este módulo não é o banco do Sentinela. É o mapa das instâncias sustentadas (Oracle, SQL Server, PostgreSQL, Redis)
        — o que o N2 olha num incidente real.
      </p>
      <div className="grid cards-3">
        {health.map((item) => (
          <div className="card" key={item.name}>
            <h3>{item.name}</h3>
            <p className="muted">
              {item.engine} · {item.host} · {item.vendor}
            </p>
            <p>
              <span className={`badge ${item.status}`}>{item.status}</span> {item.role}
            </p>
            <p>
              Sessões {item.fill}% · latência {item.latency_ms} ms
            </p>
            <div className={`bar ${item.fill > 90 ? "danger" : ""}`}>
              <span style={{ width: `${Math.min(item.fill, 100)}%` }} />
            </div>
            <p className="muted">{item.signal}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
