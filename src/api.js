const API = import.meta.env.VITE_API_URL || "";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
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
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
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
