import { useEffect, useState } from 'react';
import { Challan, FeeHead, FinanceSummary, getFinanceSummary, listChallans, listFeeHeads } from '../../services/fees';

export function FinancePage() {
  const [heads, setHeads] = useState<FeeHead[]>([]);
  const [challans, setChallans] = useState<Challan[]>([]);
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { Promise.all([listFeeHeads(), listChallans(), getFinanceSummary()]).then(([h,c,s]) => { setHeads(h); setChallans(c.items); setSummary(s); }).catch((e) => setError(e.message)); }, []);
  return <section style={{ marginTop: '2rem' }}>
    <h2>Enterprise Finance</h2>
    <p>Fee configuration, challans, collections, scholarships, installments, refunds, and financial reporting.</p>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
    {summary && <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      <strong>Collections: {summary.total_collections}</strong><strong>Outstanding: {summary.outstanding_dues}</strong><strong>Overdue: {summary.overdue_challans}</strong><strong>Scholarships: {summary.scholarships_approved}</strong>
    </div>}
    <h3>Fee Heads</h3><ul>{heads.map((h) => <li key={h.id}>{h.name} ({h.head_type})</li>)}</ul>
    <h3>Recent Challans</h3><ul>{challans.map((c) => <li key={c.id}>{c.challan_number} — {c.status} — Balance {c.balance_amount}</li>)}</ul>
  </section>;
}
