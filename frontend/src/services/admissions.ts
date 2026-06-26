export type AdmissionMode = 'online' | 'offline';
export type AdmissionStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'documents_pending'
  | 'eligible'
  | 'merit_listed'
  | 'offered'
  | 'admitted'
  | 'rejected'
  | 'cancelled';

export interface AdmissionApplicationForm {
  application_number: string;
  mode: AdmissionMode;
  applicant_first_name: string;
  applicant_last_name: string;
  date_of_birth: string;
  gender: string;
  email?: string;
  mobile?: string;
  address: string;
  guardian_name: string;
  guardian_mobile: string;
  guardian_email?: string;
  previous_school?: string;
  previous_class?: string;
  program: string;
  applying_for_class: string;
  preferred_section?: string;
  academic_session: string;
  obtained_marks?: number;
  total_marks?: number;
  documents: Array<{ document_type: string; title: string; file_path: string }>;
}

export interface AdmissionApplication extends AdmissionApplicationForm {
  id: string;
  college_id: string;
  status: AdmissionStatus;
  merit_score?: number;
  reviewed_by?: string;
  reviewed_at?: string;
  decision_reason?: string;
  admitted_student_id?: string;
  submitted_at: string;
  created_at: string;
  updated_at: string;
}

export interface AdmissionApplicationListResponse {
  items: AdmissionApplication[];
  total: number;
  limit: number;
  offset: number;
}

export interface MeritListRequest {
  title: string;
  program: string;
  academic_session: string;
  list_number: number;
  capacity: number;
  minimum_score?: number;
  offer_expires_on?: string;
}

export interface MeritList {
  id: string;
  title: string;
  program: string;
  academic_session: string;
  list_number: number;
  status: 'draft' | 'published' | 'locked';
  entries: Array<{ id: string; application_id: string; position: number; score: number }>;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const admissionHeaders = { 'Content-Type': 'application/json', 'X-Role': 'admission_officer' };

export async function listAdmissionApplications(): Promise<AdmissionApplicationListResponse> {
  const response = await fetch(`${API_BASE_URL}/admissions/applications`, {
    headers: { 'X-Role': 'admission_officer' },
  });
  if (!response.ok) {
    throw new Error('Unable to load admission applications');
  }
  return response.json();
}

export async function createAdmissionApplication(payload: AdmissionApplicationForm): Promise<AdmissionApplication> {
  const response = await fetch(`${API_BASE_URL}/admissions/applications`, {
    method: 'POST',
    headers: admissionHeaders,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unable to create admission application' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Unable to create admission application');
  }
  return response.json();
}

export async function markApplicationEligible(applicationId: string): Promise<AdmissionApplication> {
  const response = await fetch(`${API_BASE_URL}/admissions/applications/${applicationId}/decision`, {
    method: 'POST',
    headers: admissionHeaders,
    body: JSON.stringify({ status: 'eligible' }),
  });
  if (!response.ok) {
    throw new Error('Unable to mark application eligible');
  }
  return response.json();
}

export async function createMeritList(payload: MeritListRequest): Promise<MeritList> {
  const response = await fetch(`${API_BASE_URL}/admissions/merit-lists`, {
    method: 'POST',
    headers: admissionHeaders,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unable to create merit list' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Unable to create merit list');
  }
  return response.json();
}
