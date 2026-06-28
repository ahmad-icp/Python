import { useEffect, useState } from 'react';
import { DashboardResponse, getReport, getReportingDashboard, ReportResponse } from '../../services/reporting';

export function ReportingPage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getReportingDashboard().then(setDashboard).catch((e) => setError(e.message)); }, []);
  const loadReport = async (reportType: string) => { try { setReport(await getReport(reportType)); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load report'); } };
  return <section style={{ marginTop: '2rem' }}>
    <h2>Reporting & Analytics</h2>
    <p>Interactive KPIs, charts, scheduled reports, and exports for academic, attendance, examination, result, merit, financial, student, and teacher analytics.</p>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>{dashboard?.kpis.map((kpi) => <strong key={kpi.key}>{kpi.label}: {String(kpi.value)}</strong>)}</div>
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '1rem' }}>{['academic','attendance','examination','result','merit','financial','student','teacher'].map((type) => <button key={type} type="button" onClick={() => loadReport(type)}>{type}</button>)}</div>
    {report && <article><h3>{report.title}</h3><table><thead><tr>{report.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{report.rows.map((row, index) => <tr key={index}>{report.columns.map((column) => <td key={column}>{String(row[column] ?? '')}</td>)}</tr>)}</tbody></table></article>}
  </section>;
}
