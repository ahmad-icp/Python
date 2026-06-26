import { useEffect, useState } from 'react';
import { listAttendanceSessions } from '../../services/attendance';

export function AttendancePage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAttendanceSessions()
      .then((data) => setSessions(data.items ?? []))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <h2>Attendance Management</h2>
      <p>Create class attendance sessions, bulk mark records, finalize registers, and review attendance summaries.</p>
      {error ? <p role="alert">{error}</p> : null}
      <table>
        <thead><tr><th>Date</th><th>Teacher</th><th>Status</th></tr></thead>
        <tbody>{sessions.map((session) => <tr key={session.id}><td>{session.attendance_date}</td><td>{session.teacher_name}</td><td>{session.status}</td></tr>)}</tbody>
      </table>
    </section>
  );
}
