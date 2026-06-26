import { useEffect, useMemo, useState } from 'react';
import { examinationApi } from '../../services/examinations';

export function ExaminationPage() {
  const [exams, setExams] = useState<any[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([examinationApi.listExams(), examinationApi.listSchedules()])
      .then(([examData, scheduleData]) => {
        setExams(examData.items ?? []);
        setSchedules(scheduleData.items ?? []);
      })
      .catch((err) => setError(err.message));
  }, []);

  const filteredExams = useMemo(() => exams.filter((exam) => {
    const matchesText = exam.name.toLowerCase().includes(query.toLowerCase());
    const matchesStatus = status ? exam.status === status : true;
    return matchesText && matchesStatus;
  }), [exams, query, status]);

  return (
    <section style={{ display: 'grid', gap: '1rem' }}>
      <header>
        <h2>Examination Dashboard</h2>
        <p>Configure exam types, assessment components, schedules, halls, invigilators, publishing, and locking.</p>
      </header>
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        <input aria-label="Search exams" placeholder="Search exams" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select aria-label="Filter by status" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="scheduled">Scheduled</option>
          <option value="published">Published</option>
          <option value="locked">Locked</option>
        </select>
      </div>
      {error ? <p role="alert">{error}</p> : null}
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Exam</th><th>Status</th><th>Start</th><th>End</th></tr></thead>
          <tbody>{filteredExams.map((exam) => <tr key={exam.id}><td>{exam.name}</td><td>{exam.status}</td><td>{exam.start_date}</td><td>{exam.end_date}</td></tr>)}</tbody>
        </table>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <h3>Calendar View</h3>
        <table>
          <thead><tr><th>Date</th><th>Subject</th><th>Component</th><th>Time</th><th>Hall</th></tr></thead>
          <tbody>{schedules.map((schedule) => <tr key={schedule.id}><td>{schedule.exam_date}</td><td>{schedule.subject_id}</td><td>{schedule.component_type}</td><td>{schedule.start_time} - {schedule.end_time}</td><td>{schedule.hall_id}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}
