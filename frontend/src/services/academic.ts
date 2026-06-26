export interface Institution { id: string; college_id: string; name: string; code: string; address?: string; is_active: boolean }
export interface AcademicSession { id: string; college_id: string; name: string; start_date: string; end_date: string; status: 'planned' | 'active' | 'archived'; is_locked: boolean }
export interface Department { id: string; college_id: string; institution_id: string; campus_id?: string; name: string; code: string; is_active: boolean }
export interface Program { id: string; college_id: string; department_id: string; name: string; code: string; duration_years: number; is_active: boolean }
export interface AcademicClass { id: string; college_id: string; program_id: string; session_id: string; name: string; display_order: number; is_archived: boolean }
export interface Section { id: string; college_id: string; class_id: string; name: string; capacity: number; enrolled_count: number; room?: string; is_active: boolean }
export interface Subject { id: string; college_id: string; department_id?: string; code: string; name: string; credit_hours: number; weekly_periods: number; is_elective: boolean; is_active: boolean }
export interface TeacherAssignment { id: string; college_id: string; teacher_id: string; teacher_name: string; section_id: string; subject_id: string; weekly_periods: number; max_weekly_periods: number; status: 'active' | 'archived' }
export interface ListResponse<T> { items: T[]; total: number; limit: number; offset: number }

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/academic${path}`, { ...options, headers: { ...headers, ...(options.headers ?? {}) } });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Academic request failed' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Academic request failed');
  }
  return response.json();
}

export const academicApi = {
  listInstitutions: (search = '') => request<ListResponse<Institution>>(`/institutions?search=${encodeURIComponent(search)}`),
  createInstitution: (payload: { name: string; code: string; address?: string }) => request<Institution>('/institutions', { method: 'POST', body: JSON.stringify(payload) }),
  listSessions: () => request<ListResponse<AcademicSession>>('/sessions'),
  createSession: (payload: { name: string; start_date: string; end_date: string; status: string }) => request<AcademicSession>('/sessions', { method: 'POST', body: JSON.stringify(payload) }),
  listDepartments: () => request<ListResponse<Department>>('/departments'),
  createDepartment: (payload: { institution_id: string; name: string; code: string; campus_id?: string }) => request<Department>('/departments', { method: 'POST', body: JSON.stringify(payload) }),
  listPrograms: () => request<ListResponse<Program>>('/programs'),
  createProgram: (payload: { department_id: string; name: string; code: string; duration_years: number }) => request<Program>('/programs', { method: 'POST', body: JSON.stringify(payload) }),
  listClasses: () => request<ListResponse<AcademicClass>>('/classes'),
  createClass: (payload: { program_id: string; session_id: string; name: string; display_order: number }) => request<AcademicClass>('/classes', { method: 'POST', body: JSON.stringify(payload) }),
  listSections: () => request<ListResponse<Section>>('/sections'),
  createSection: (payload: { class_id: string; name: string; capacity: number; enrolled_count: number; room?: string }) => request<Section>('/sections', { method: 'POST', body: JSON.stringify(payload) }),
  listSubjects: () => request<ListResponse<Subject>>('/subjects'),
  createSubject: (payload: { department_id?: string; code: string; name: string; credit_hours: number; weekly_periods: number; is_elective: boolean; prerequisite_subject_ids: string[] }) => request<Subject>('/subjects', { method: 'POST', body: JSON.stringify(payload) }),
  listTeacherAssignments: () => request<ListResponse<TeacherAssignment>>('/teacher-assignments'),
  createTeacherAssignment: (payload: { teacher_id: string; teacher_name: string; section_id: string; subject_id: string; weekly_periods: number; max_weekly_periods: number }) => request<TeacherAssignment>('/teacher-assignments', { method: 'POST', body: JSON.stringify(payload) }),
};
