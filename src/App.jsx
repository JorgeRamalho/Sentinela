import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Monitoring from "./pages/Monitoring.jsx";
import Incidents from "./pages/Incidents.jsx";
import Tickets from "./pages/Tickets.jsx";
import LogAnalyzer from "./pages/LogAnalyzer.jsx";
import Automation from "./pages/Automation.jsx";
import Databases from "./pages/Databases.jsx";
import Vendors from "./pages/Vendors.jsx";
import Knowledge from "./pages/Knowledge.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/monitoramento" element={<Monitoring />} />
        <Route path="/incidentes" element={<Incidents />} />
        <Route path="/chamados" element={<Tickets />} />
        <Route path="/logs" element={<LogAnalyzer />} />
        <Route path="/automacao" element={<Automation />} />
        <Route path="/banco" element={<Databases />} />
        <Route path="/fornecedores" element={<Vendors />} />
        <Route path="/conhecimento" element={<Knowledge />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
