export async function apiFetch(path, options = {}) {
  const response = await fetch(path, options);
  const text = await response.text();
  let payload = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (_error) {
      payload = text;
    }
  }

  if (!response.ok) {
    const detail =
      (payload && typeof payload === "object" && payload.detail) ||
      response.statusText ||
      "Request failed";
    throw new Error(String(detail));
  }

  return payload;
}

export function toBearerHeaders(accessToken, extraHeaders = {}) {
  if (!accessToken) {
    return { ...extraHeaders };
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    ...extraHeaders,
  };
}
