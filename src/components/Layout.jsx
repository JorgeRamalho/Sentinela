import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../api.js";

const NAV = [
  { to: "/", label: "Dashboard", icon: "◉" },
  { to: "/monitoramento", label: "Monitoramento", icon: "▣" },
  { to: "/incidentes", label: "Incidentes", icon: "⚠" },
  { to: "/chamados", label: "Chamados", icon: "▤" },
  { to: "/logs", label: "Analisador de logs", icon: "≡" },
  { to: "/automacao", label: "Automação N1/N2", icon: "⟳" },
  { to: "/banco", label: "Banco de dados", icon: "▦" },
  { to: "/fornecedores", label: "Fornecedores", icon: "⬡" },
  { to: "/conhecimento", label: "Base de conhecimento", icon: "◎" },
];

export default function Layout() {
  const [meta, setMeta] = useState({ simulate: true, env: "demo", app: "Sentinela" });
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    api("/api/meta")
      .then(setMeta)
      .catch(() => setOffline(true));
  }, []);

  return (
    <div className="shell">
      <aside className="side">
        <div className="brand">
          <div className="radar" aria-hidden="true" />
          <div>
            <strong>SENTINELA</strong>
            <span>Sustentação N1 / N2</span>
          </div>
        </div>
        <nav>
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"}>
              <i>{item.icon}</i>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <footer>
          Pipeline Jenkins · Docker
          <small>Audit trail ativo</small>
        </footer>
      </aside>
      <div className="main">
        <header className="top">
          <div>
            <p className="kicker">Console operacional</p>
            <h1>Ambiente de sustentação</h1>
          </div>
          <div className="top-meta">
            {offline && (
              <span className="pill warn" title="Confira o serviço /api na hospedagem">
                API indisponível — backend não responde
              </span>
            )}
            <span className={`pill ${meta.simulate ? "ok" : "danger"}`}>
              {meta.simulate ? "SIMULAR = true" : "EXECUÇÃO REAL"}
            </span>
            <span className="pill">{meta.env}</span>
          </div>
        </header>
        <Outlet />
      </div>
    </div>
  );
}
