import { palette } from '../theme/colors';

// The one and only network entry point for this app. Everything that talks to
// the Fieldnote backend goes through this module — screens and components must
// not call fetch directly.
const BASE_URL = 'https://api.fieldnote.example/v1';

let sessionToken: string | null = null;

export function setSessionToken(token: string | null) {
  sessionToken = token;
}

async function request(path: string, options: RequestInit = {}) {
  const headers = { ...(options.headers || {}) } as Record<string, string>;
  if (sessionToken) headers.Authorization = `Bearer ${sessionToken}`;
  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) throw new Error(`request failed: ${path} (${response.status})`);
  return response.json();
}

export function fetchSightings() {
  return request('/sightings');
}

export function createSighting(payload: Record<string, unknown>) {
  return request('/sightings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
