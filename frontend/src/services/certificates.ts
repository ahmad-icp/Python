export type CertificateStatus = 'draft'|'pending_approval'|'approved'|'rejected'|'issued'|'revoked';
export interface CertificateRequest { id:string; certificate_type:string; student_id?:string; employee_id?:string; purpose:string; status:CertificateStatus; verification_code:string; created_at:string; }
export interface CertificateListResponse { items:CertificateRequest[]; total:number; limit:number; offset:number; }
export interface DocumentItem { id:string; owner_type:string; owner_id:string; document_type:string; title:string; approval_status:string; created_at:string; }
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };
export async function listCertificateRequests(): Promise<CertificateListResponse> { const r=await fetch(`${API_BASE_URL}/certificates/requests`, { headers }); if(!r.ok) throw new Error('Unable to load certificates'); return r.json(); }
export async function listDocuments(): Promise<DocumentItem[]> { const r=await fetch(`${API_BASE_URL}/certificates/documents`, { headers }); if(!r.ok) throw new Error('Unable to load documents'); return r.json(); }
