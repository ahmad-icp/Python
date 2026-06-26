export interface AttendanceSessionPayload {
  session_id: string;
  section_id: string;
  attendance_date: string;
  teacher_id: string;
  teacher_name: string;
  time_slot_id?: string;
  timetable_entry_id?: string;
  remarks?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export async function listAttendanceSessions() {
  const response = await fetch(`${API_BASE}/attendance/sessions`);
  if (!response.ok) throw new Error('Unable to load attendance sessions');
  return response.json();
}

export async function createAttendanceSession(payload: AttendanceSessionPayload) {
  const response = await fetch(`${API_BASE}/attendance/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Unable to create attendance session');
  return response.json();
}
