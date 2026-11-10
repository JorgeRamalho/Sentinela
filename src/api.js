const API = import.meta.env.VITE_API_URL || "";
const DEMO_MODE = import.meta.env.PROD && !API;

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function demoFixtureUrl(path, method = "GET") {
  const qIndex = path.indexOf("?");
  const pathOnly = qIndex >= 0 ? path.slice(0, qIndex) : path;
  const search = qIndex >= 0 ? path.slice(qIndex) : "";
  const segments = pathOnly
    .replace(/^\/api\/?/, "")
    .split("/")
    .filter(Boolean);
  const suffix = segments.length ? segments.join("__") : "meta";
  const prefix = method === "GET" || method === "HEAD" ? "api" : "post";
  return `/demo-api/${prefix}__${suffix}.json${search}`;
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

async function readBody(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }
  const contentType = response.headers.get("content-type") || "";
  const looksJson =
    contentType.includes("application/json") ||
    text.trimStart().startsWith("{") ||
    text.trimStart().startsWith("[");
  if (!looksJson) {
    return text;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const url = DEMO_MODE ? demoFixtureUrl(path, method) : `${API}${path}`;
  const fetchMethod = DEMO_MODE && method !== "GET" && method !== "HEAD" ? "GET" : method;

  const response = await fetch(url, {
    ...options,
    method: fetchMethod,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let body = await readBody(response);
  if (!response.ok) {
    let detail = response.statusText;
    if (body && typeof body === "object" && body.detail !== undefined) {
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } else if (typeof body === "string" && body.trim()) {
      detail = body.trim();
    }
    throw new ApiError(detail, response.status);
  }

  if (DEMO_MODE && method === "GET" && path.startsWith("/api/knowledge")) {
    const qIndex = path.indexOf("?");
    const search = qIndex >= 0 ? path.slice(qIndex + 1) : "";
    const params = new URLSearchParams(search);
    const q = params.get("q") || "";
    if (Array.isArray(body)) {
      body = filterKnowledge(body, q);
    }
  }

  return body;
}
