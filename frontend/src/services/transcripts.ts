export interface TranscriptPayload { student_id: string; institution_name: string; remarks?: string; }
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
async function request(path:string, options?:RequestInit){const response=await fetch(`${API_BASE}${path}`,options); if(!response.ok) throw new Error(`Transcript request failed: ${response.status}`); return response.json();}
export const transcriptsApi={list:(query='')=>request(`/transcripts/${query}`),generate:(payload:TranscriptPayload)=>request('/transcripts/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),issue:(id:string)=>request(`/transcripts/${id}/issue`,{method:'POST'}),verify:(code:string)=>request(`/transcripts/verify/${code}`)};
