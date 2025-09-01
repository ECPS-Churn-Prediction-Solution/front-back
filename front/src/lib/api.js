const USE_DIRECT = import.meta.env.VITE_USE_DIRECT_API === '1';
const API_BASE_URL = USE_DIRECT ? (import.meta.env.VITE_API_BASE_URL || '') : '';

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const headers = new Headers(options.headers || {});
  const init = { ...options, headers, credentials: 'include' };

  if (init.body && typeof init.body === 'object' && !(init.body instanceof FormData)) {
    if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
    init.body = JSON.stringify(init.body);
  }

  const res = await fetch(url, init);
  let data = null;
  const contentType = res.headers.get('Content-Type') || '';
  if (contentType.includes('application/json')) {
    data = await res.json().catch(() => null);
  } else {
    data = await res.text().catch(() => null);
  }

  if (!res.ok) {
    if (options.silent401 && res.status === 401) {
      return null;
    }
    const message = (data && (data.detail || data.message)) || `Request failed: ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}


