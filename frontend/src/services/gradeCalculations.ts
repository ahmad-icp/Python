export interface GradeMappingPayload { grade: string; min_percentage: number; max_percentage: number; grade_point?: number; remark?: string; is_passing?: boolean; }
export interface GradeSystemPayload { name: string; system_type: 'gpa' | 'percentage'; scope_type?: 'institution' | 'program' | 'class' | 'section'; scope_id?: string; version?: number; gpa_scale?: number; passing_percentage?: number; passing_gpa?: number; decimal_places?: number; rounding_mode?: 'standard' | 'floor' | 'ceil'; is_active?: boolean; mappings: GradeMappingPayload[]; }
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
async function request(path: string, options?: RequestInit) { const response = await fetch(`${API_BASE}${path}`, options); if (!response.ok) throw new Error(`Grade calculation request failed: ${response.status}`); return response.json(); }
export const gradeCalculationApi = {
  listSystems: () => request('/grade-calculations/systems'),
  createSystem: (payload: GradeSystemPayload) => request('/grade-calculations/systems', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  calculate: (result_ids: string[], system_id?: string) => request('/grade-calculations/calculations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ result_ids, system_id, force_recalculate: true }) }),
  listCalculations: (query = '') => request(`/grade-calculations/calculations${query}`),
};
