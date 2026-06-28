export interface KPIWidget { key:string; label:string; value:number|string; trend?:string; }
export interface ChartDefinition { key:string; title:string; chart_type:string; labels:string[]; series:Array<{label:string; data:number[]}>; }
export interface DashboardResponse { kpis:KPIWidget[]; charts:ChartDefinition[]; }
export interface ReportResponse { report_type:string; title:string; columns:string[]; rows:Array<Record<string, string|number|null>>; generated_at:string; }
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };
export async function getReportingDashboard(): Promise<DashboardResponse> { const r=await fetch(`${API_BASE_URL}/reporting/dashboard`, { headers }); if(!r.ok) throw new Error('Unable to load reporting dashboard'); return r.json(); }
export async function getReport(reportType:string): Promise<ReportResponse> { const r=await fetch(`${API_BASE_URL}/reporting/${reportType}`, { headers }); if(!r.ok) throw new Error('Unable to load report'); return r.json(); }
