export interface ReportCardPayload { result_id: string; grade_calculation_id?: string; institution_name: string; branding?: Record<string, string>; remarks?: string; }
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
async function request(path: string, options?: RequestInit) { const response = await fetch(`${API_BASE}${path}`, options); if (!response.ok) throw new Error(`Report card request failed: ${response.status}`); return response.json(); }
export const reportCardsApi = {
  list: (query = '') => request(`/report-cards/${query}`),
  generate: (payload: ReportCardPayload) => request('/report-cards/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  issue: (id: string) => request(`/report-cards/${id}/issue`, { method: 'POST' }),
  verify: (code: string) => request(`/report-cards/verify/${code}`),
};
