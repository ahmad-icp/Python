import { useEffect, useState } from 'react';
import { resultsApi } from '../../services/results';

export function ResultProcessingPage() {
  const [results, setResults] = useState<any[]>([]);
  const [examId, setExamId] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState<string | null>(null);
  const load = async () => {
    const params = new URLSearchParams();
    if (examId) params.set('exam_id', examId);
    if (status) params.set('status_filter', status);
    const data = await resultsApi.listResults(params.toString() ? `?${params}` : '');
    setResults(data.items ?? []);
  };
  useEffect(() => { load().catch((e) => setError(e.message)); }, []);
  const calculate = async () => { setError(null); await resultsApi.calculate({ exam_id: examId, force_recalculate: true }); await load(); };
  return <section style={{ border: '1px solid #d7dce2', borderRadius: 12, padding: '1rem', marginBlock: '1rem' }}>
    <h2>Result Processing</h2>
    <p>Calculate, publish, lock, and track student results from locked marks-entry batches.</p>
    <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap' }}>
      <input aria-label="Exam ID" placeholder="Exam ID" value={examId} onChange={(e) => setExamId(e.target.value)} />
      <select aria-label="Result status" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">All statuses</option><option value="draft">Draft</option><option value="published">Published</option><option value="locked">Locked</option></select>
      <button onClick={load}>Search</button><button disabled={!examId} onClick={calculate}>Calculate / Recalculate</button>
    </div>
    {error && <p role="alert" style={{ color: '#b42318' }}>{error}</p>}
    <div style={{ overflowX: 'auto', marginTop: '1rem' }}><table><thead><tr><th>Student</th><th>Status</th><th>Outcome</th><th>Obtained</th><th>%</th><th>Promotion</th><th>Actions</th></tr></thead><tbody>{results.map((r) => <tr key={r.id}><td>{r.student_id}</td><td>{r.status}</td><td>{r.outcome}</td><td>{r.obtained_marks}/{r.total_marks}</td><td>{r.percentage}</td><td>{r.is_promotion_eligible ? 'Eligible' : 'Not eligible'}</td><td><button disabled={r.status !== 'draft'} onClick={async()=>{await resultsApi.publish(r.id); await load();}}>Publish</button><button disabled={r.status !== 'published'} onClick={async()=>{await resultsApi.lock(r.id); await load();}}>Lock</button></td></tr>)}</tbody></table></div>
  </section>;
}
