export interface MarksBatchPayload {
  exam_id: string;
  section_id: string;
  subject_id: string;
  component_id: string;
}

export interface MarksEntryPayload {
  student_id: string;
  marks_obtained: number;
  moderation_marks?: number;
  recheck_notes?: string;
  remarks?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request(path: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) throw new Error(`Marks entry request failed: ${response.status}`);
  return response.json();
}

export const marksEntryApi = {
  listBatches: () => request('/marks-entry/batches'),
  createBatch: (payload: MarksBatchPayload) => request('/marks-entry/batches', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listEntries: (batchId?: string) => request(`/marks-entry/entries${batchId ? `?batch_id=${batchId}` : ''}`),
  bulkUpsert: (batchId: string, entries: MarksEntryPayload[]) => request(`/marks-entry/batches/${batchId}/entries`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entries }) }),
  importMarks: (batchId: string, content: string, format: 'csv' | 'excel') => request(`/marks-entry/batches/${batchId}/import`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content, format }) }),
  submit: (batchId: string) => request(`/marks-entry/batches/${batchId}/submit`, { method: 'POST' }),
  lock: (batchId: string) => request(`/marks-entry/batches/${batchId}/lock`, { method: 'POST' }),
};
