import { readDemoFixture } from "./demo-fixtures.js";

const API = import.meta.env.VITE_API_URL || "";
const DEMO_MODE = import.meta.env.PROD && !API;

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
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

function applyKnowledgeFilter(body, path) {
  if (!path.startsWith("/api/knowledge")) {
    return body;
  }
  const qIndex = path.indexOf("?");
  if (qIndex < 0) {
    return body;
  }
  const params = new URLSearchParams(path.slice(qIndex + 1));
  const q = params.get("q") || "";
  if (!Array.isArray(body)) {
    return body;
  }
  return filterKnowledge(body, q);
}

export async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();

  if (DEMO_MODE) {
    try {
      let body = readDemoFixture(path, method);
      body = applyKnowledgeFilter(body, path);
      return body;
    } catch (err) {
      throw new ApiError(err.message, 404);
    }
  }

  const response = await fetch(`${API}${path}`, {
    ...options,
    method,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await readBody(response);
  if (!response.ok) {
    let detail = response.statusText;
    if (body && typeof body === "object" && body.detail !== undefined) {
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } else if (typeof body === "string" && body.trim()) {
      detail = body.trim();
    }
    throw new ApiError(detail, response.status);
  }
  return body;
}
