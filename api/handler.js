import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FIXTURE_DIR = join(dirname(fileURLToPath(import.meta.url)), "_fixtures");

function pathSegments(pathname) {
  const pathOnly = pathname.split("?")[0];
  return pathOnly
    .replace(/^\/api\/?/, "")
    .split("/")
    .filter(Boolean);
}

function fixtureFile(method, segments) {
  const suffix = segments.length ? segments.join("__") : "meta";
  const prefix = method === "GET" || method === "HEAD" ? "api" : "post";
  return join(FIXTURE_DIR, `${prefix}__${suffix}.json`);
}

function filterKnowledge(rows, query) {
  const term = query?.trim().toLowerCase();
  if (!term) {
    return rows;
  }
  return rows.filter((row) => {
    const hay = `${row.title || ""} ${row.tags || ""} ${row.category || ""}`.toLowerCase();
    return hay.includes(term);
  });
}

export default function handler(req, res) {
  const pathname = (req.url || "/api/meta").split("?")[0];
  const method = req.method || "GET";
  const segments = pathSegments(pathname);
  const file = fixtureFile(method, segments);

  if (!existsSync(file)) {
    res.status(404).json({ detail: `Demo API sem fixture: ${method} ${pathname}` });
    return;
  }

  let body = readFileSync(file, "utf8");

  if (method === "GET" && pathname.startsWith("/api/knowledge")) {
    const query = new URL(req.url, "http://localhost").searchParams.get("q") || "";
    const rows = JSON.parse(body);
    const filtered = filterKnowledge(rows, query);
    body = JSON.stringify(filtered);
  }

  res.setHeader("Content-Type", "application/json");
  res.status(200).end(body);
}
