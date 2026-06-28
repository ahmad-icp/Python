import { useState } from 'react';
import { getParentPortal, getStudentPortal, getTeacherPortal, ParentPortalDashboard, StudentPortalDashboard, TeacherPortalDashboard } from '../../services/portals';

export function PortalsPage() {
  const [studentId, setStudentId] = useState('');
  const [student, setStudent] = useState<StudentPortalDashboard | null>(null);
  const [parent, setParent] = useState<ParentPortalDashboard | null>(null);
  const [teacher, setTeacher] = useState<TeacherPortalDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = async (kind: 'student'|'parent'|'teacher') => {
    setError(null);
    try {
      if (kind === 'student') setStudent(await getStudentPortal(studentId));
      if (kind === 'parent') setParent(await getParentPortal());
      if (kind === 'teacher') setTeacher(await getTeacherPortal());
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load portal'); }
  };
  return <section style={{ marginTop: '2rem' }}>
    <h2>User Portals</h2>
    <p>Role-specific dashboards for students, parents, and teachers.</p>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      <input placeholder="Student ID" value={studentId} onChange={(event) => setStudentId(event.target.value)} />
      <button type="button" onClick={() => load('student')} disabled={!studentId}>Load Student Portal</button>
      <button type="button" onClick={() => load('parent')}>Load Parent Portal</button>
      <button type="button" onClick={() => load('teacher')}>Load Teacher Portal</button>
    </div>
    {student && <article><h3>{student.profile.first_name} {student.profile.last_name}</h3><p>Attendance: {student.attendance.percentage}% · Challans: {student.challans.length} · Results: {student.results.length}</p></article>}
    {parent && <article><h3>Parent Portal</h3><p>Children loaded: {parent.children.length}</p></article>}
    {teacher && <article><h3>Teacher Portal</h3><p>Timetable entries: {teacher.timetable.length} · Attendance sessions: {teacher.attendance_sessions.length}</p></article>}
  </section>;
}
