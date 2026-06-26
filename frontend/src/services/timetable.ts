export interface Classroom { id: string; name: string; code: string; room_type: string; capacity: number; is_active: boolean }
export interface TimeSlot { id: string; name: string; start_time: string; end_time: string; sort_order: number; is_break: boolean }
export interface TimetableVersion { id: string; session_id: string; section_id: string; version_number: number; status: 'draft' | 'published' | 'archived'; effective_from: string; effective_to: string; created_by: string }
export interface TimetableEntry { id: string; version_id: string; session_id: string; section_id: string; subject_id: string; teacher_id: string; teacher_name: string; classroom_id: string; time_slot_id: string; weekday: number; entry_type: string; notes?: string }
export interface ListResponse<T> { items: T[]; total: number; limit: number; offset: number }

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/timetable${path}`, { ...options, headers: { ...headers, ...(options.headers ?? {}) } });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Timetable request failed' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Timetable request failed');
  }
  return response.json();
}

export const timetableApi = {
  listClassrooms: () => request<ListResponse<Classroom>>('/classrooms'),
  createClassroom: (payload: { name: string; code: string; room_type: string; capacity: number }) => request<Classroom>('/classrooms', { method: 'POST', body: JSON.stringify(payload) }),
  listTimeSlots: () => request<ListResponse<TimeSlot>>('/time-slots'),
  createTimeSlot: (payload: { name: string; start_time: string; end_time: string; sort_order: number; is_break: boolean }) => request<TimeSlot>('/time-slots', { method: 'POST', body: JSON.stringify(payload) }),
  listVersions: () => request<ListResponse<TimetableVersion>>('/versions'),
  createVersion: (payload: { session_id: string; section_id: string; effective_from: string; effective_to: string }) => request<TimetableVersion>('/versions', { method: 'POST', body: JSON.stringify(payload) }),
  publishVersion: (versionId: string) => request<TimetableVersion>(`/versions/${versionId}/publish`, { method: 'POST' }),
  listEntries: () => request<ListResponse<TimetableEntry>>('/entries'),
  createEntry: (payload: { version_id: string; subject_id: string; teacher_id: string; teacher_name: string; classroom_id: string; time_slot_id: string; weekday: number; entry_type: string }) => request<TimetableEntry>('/entries', { method: 'POST', body: JSON.stringify(payload) }),
};
