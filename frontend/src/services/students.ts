export type StudentStatus = 'applicant' | 'active' | 'suspended' | 'withdrawn' | 'graduated' | 'alumni';

export interface GuardianForm {
  full_name: string;
  relationship: 'father' | 'mother' | 'guardian' | 'other';
  mobile: string;
  email?: string;
  occupation?: string;
  is_primary: boolean;
}

export interface StudentForm {
  admission_number: string;
  roll_number?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email?: string;
  mobile?: string;
  address: string;
  program: string;
  current_class: string;
  current_section?: string;
  academic_session: string;
  enrollment_date: string;
  guardians: GuardianForm[];
}

export interface Student extends StudentForm {
  id: string;
  college_id: string;
  status: StudentStatus;
  documents: Array<{
    id: string;
    document_type: string;
    title: string;
    file_path: string;
    verification_status: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface StudentListResponse {
  items: Student[];
  total: number;
  limit: number;
  offset: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export async function listStudents(): Promise<StudentListResponse> {
  const response = await fetch(`${API_BASE_URL}/students`, {
    headers: { 'X-Role': 'administrator' },
  });
  if (!response.ok) {
    throw new Error('Unable to load students');
  }
  return response.json();
}

export async function createStudent(payload: StudentForm): Promise<Student> {
  const response = await fetch(`${API_BASE_URL}/students`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Role': 'administrator' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unable to create student' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Unable to create student');
  }
  return response.json();
}
