export type FeeHeadType = 'tuition'|'admission'|'exam'|'lab'|'library'|'transport'|'hostel'|'miscellaneous';
export interface FeeHead { id:string; college_id:string; code:string; name:string; head_type:FeeHeadType; is_refundable:boolean; is_active:boolean; created_at:string; }
export interface Challan { id:string; challan_number:string; student_id:string; billing_period:string; due_date:string; status:string; total_amount:string; paid_amount:string; balance_amount:string; }
export interface ChallanListResponse { items: Challan[]; total:number; limit:number; offset:number; }
export interface FinanceSummary { total_collections:string; outstanding_dues:string; overdue_challans:number; scholarships_approved:number; }
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };
export async function listFeeHeads(): Promise<FeeHead[]> { const r=await fetch(`${API_BASE_URL}/fees/heads`,{headers}); if(!r.ok) throw new Error('Unable to load fee heads'); return r.json(); }
export async function listChallans(): Promise<ChallanListResponse> { const r=await fetch(`${API_BASE_URL}/fees/challans`,{headers}); if(!r.ok) throw new Error('Unable to load challans'); return r.json(); }
export async function getFinanceSummary(): Promise<FinanceSummary> { const r=await fetch(`${API_BASE_URL}/fees/reports/summary`,{headers}); if(!r.ok) throw new Error('Unable to load finance summary'); return r.json(); }
