import { useEffect, useState } from 'react';
import { gradeCalculationApi } from '../../services/gradeCalculations';

export function GradeCalculationPage() {
  const [items, setItems] = useState<any[]>([]);
  const [studentId, setStudentId] = useState('');
  const [examId, setExamId] = useState('');
  const [resultIds, setResultIds] = useState('');
  const [systemId, setSystemId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const load = async () => {
    const params = new URLSearchParams();
    if (studentId) params.set('student_id', studentId);
    if (examId) params.set('exam_id', examId);
    const data = await gradeCalculationApi.listCalculations(params.toString() ? `?${params}` : '');
    setItems(data.items ?? []);
  };
  useEffect(() => { load().catch((e) => setError(e.message)); }, []);
  const calculate = async () => {
    setError(null);
    const ids = resultIds.split(',').map((id) => id.trim()).filter(Boolean);
    if (!ids.length) { setError('Enter at least one result ID.'); return; }
    await gradeCalculationApi.calculate(ids, systemId || undefined);
    await load();
  };
  return <section style={{ border: '1px solid #d7dce2', borderRadius: 12, padding: '1rem', marginBlock: '1rem' }}>
    <h2>GPA & Percentage Calculation</h2>
    <p>Map published results to institution/program grading systems with GPA, CGPA, percentage, grade, and academic standing.</p>
    <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap' }}>
      <input aria-label="Result IDs" placeholder="Result IDs, comma-separated" value={resultIds} onChange={(e) => setResultIds(e.target.value)} />
      <input aria-label="Grade system ID" placeholder="Grade system ID (optional)" value={systemId} onChange={(e) => setSystemId(e.target.value)} />
      <button onClick={calculate}>Calculate</button>
    </div>
    <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap', marginTop: '.75rem' }}>
      <input aria-label="Student ID" placeholder="Student ID filter" value={studentId} onChange={(e) => setStudentId(e.target.value)} />
      <input aria-label="Exam ID" placeholder="Exam ID filter" value={examId} onChange={(e) => setExamId(e.target.value)} />
      <button onClick={load}>Search</button>
    </div>
    {error && <p role="alert" style={{ color: '#b42318' }}>{error}</p>}
    <div style={{ overflowX: 'auto', marginTop: '1rem' }}><table><thead><tr><th>Student</th><th>Percentage</th><th>Grade</th><th>GPA</th><th>CGPA</th><th>Standing</th><th>Promotion</th></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td>{item.student_id}</td><td>{item.percentage}</td><td>{item.grade}</td><td>{item.gpa ?? 'N/A'}</td><td>{item.cgpa ?? 'N/A'}</td><td>{item.academic_standing}</td><td>{item.is_promotion_eligible ? 'Eligible' : 'Not eligible'}</td></tr>)}</tbody></table></div>
  </section>;
}
