// The one shared fetch helper. Every request the web app makes to the API goes
// through postData/fetchData here — components must never call fetch directly.
const TEAM_PASSPHRASE = import.meta.env.VITE_TEAM_PASSPHRASE;

async function request(path: string, options: RequestInit = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: {
      'X-Team-Passphrase': TEAM_PASSPHRASE,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  if (!response.ok) throw new Error(`api ${path} -> ${response.status}`);
  return response.json();
}

export function fetchData<T>(path: string): Promise<T> {
  return request(path);
}

export function postData<T>(path: string, body: unknown): Promise<T> {
  return request(path, { method: 'POST', body: JSON.stringify(body) });
}
