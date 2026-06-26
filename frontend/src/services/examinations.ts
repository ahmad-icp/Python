export interface ExamTypePayload {
  code: string;
  name: string;
  description?: string;
  default_weightage?: number;
}

export interface ExamPayload {
  exam_type_id: string;
  session_id: string;
  class_id: string;
  section_id: string;
  program_id?: string;
  name: string;
  start_date: string;
  end_date: string;
}

export interface ExamSchedulePayload {
  exam_id: string;
  subject_id: string;
  hall_id: string;
  component_type: string;
  exam_date: string;
  start_time: string;
  end_time: string;
  instructions?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request(path: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

export const examinationApi = {
  listTypes: () => request('/examinations/types'),
  createType: (payload: ExamTypePayload) => request('/examinations/types', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listExams: () => request('/examinations/exams'),
  createExam: (payload: ExamPayload) => request('/examinations/exams', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listSchedules: () => request('/examinations/schedules'),
  createSchedule: (payload: ExamSchedulePayload) => request('/examinations/schedules', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listHalls: () => request('/examinations/halls'),
  listInvigilators: () => request('/examinations/invigilators'),
};
