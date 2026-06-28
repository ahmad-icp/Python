export type NotificationStatus = 'queued' | 'scheduled' | 'sent' | 'failed' | 'cancelled';
export interface NotificationItem { id:string; recipient_type:string; recipient_id:string; channel:string; event_type:string; subject?:string; body:string; status:NotificationStatus; retry_count:number; created_at:string; }
export interface NotificationListResponse { items: NotificationItem[]; total:number; limit:number; offset:number; }
export interface TemplateItem { id:string; code:string; name:string; event_type:string; channel:string; is_active:boolean; }
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const headers = { 'Content-Type': 'application/json', 'X-Role': 'administrator' };
export async function listNotifications(): Promise<NotificationListResponse> { const r = await fetch(`${API_BASE_URL}/notifications`, { headers }); if (!r.ok) throw new Error('Unable to load notifications'); return r.json(); }
export async function listNotificationTemplates(): Promise<TemplateItem[]> { const r = await fetch(`${API_BASE_URL}/notifications/templates`, { headers }); if (!r.ok) throw new Error('Unable to load templates'); return r.json(); }
export async function processNotificationQueue(): Promise<{processed:number; sent:number; failed:number}> { const r = await fetch(`${API_BASE_URL}/notifications/queue/process`, { method:'POST', headers }); if (!r.ok) throw new Error('Unable to process queue'); return r.json(); }
