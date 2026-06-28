export interface ResultPolicyPayload { name: string; version?: number; minimum_percentage?: number; grace_marks?: number; promotion_minimum_percentage?: number; is_active?: boolean; }
export interface CalculateResultPayload { exam_id: string; student_ids?: string[]; policy_id?: string; force_recalculate?: boolean; }
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
async function request(path: string, options?: RequestInit) { const response = await fetch(`${API_BASE}${path}`, options); if (!response.ok) throw new Error(`Result request failed: ${response.status}`); return response.json(); }
export const resultsApi = {
  listPolicies: () => request('/results/policies'),
  createPolicy: (payload: ResultPolicyPayload) => request('/results/policies', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  calculate: (payload: CalculateResultPayload) => request('/results/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listResults: (query = '') => request(`/results/results${query}`),
  publish: (id: string) => request(`/results/results/${id}/publish`, { method: 'POST' }),
  lock: (id: string) => request(`/results/results/${id}/lock`, { method: 'POST' }),
};
