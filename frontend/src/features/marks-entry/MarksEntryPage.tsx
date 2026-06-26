import { useEffect, useMemo, useState } from 'react';
import { marksEntryApi } from '../../services/marksEntry';

export function MarksEntryPage() {
  const [batches, setBatches] = useState<any[]>([]);
  const [entries, setEntries] = useState<any[]>([]);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    marksEntryApi.listBatches()
      .then((data) => setBatches(data.items ?? []))
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selectedBatch) return;
    marksEntryApi.listEntries(selectedBatch)
      .then((data) => setEntries(data.items ?? []))
      .catch((err) => setError(err.message));
  }, [selectedBatch]);

  const filteredEntries = useMemo(() => entries.filter((entry) => entry.student_id.toLowerCase().includes(query.toLowerCase())), [entries, query]);

  return (
    <section style={{ display: 'grid', gap: '1rem' }}>
      <header>
        <h2>Marks Entry</h2>
        <p>Enter, import, validate, submit, lock, and audit theory, practical, viva, assignment, internal, and attendance marks.</p>
      </header>
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        <select aria-label="Marks batch" value={selectedBatch} onChange={(event) => setSelectedBatch(event.target.value)}>
          <option value="">Select batch</option>
          {batches.map((batch) => <option key={batch.id} value={batch.id}>{batch.subject_id} · {batch.status}</option>)}
        </select>
        <input aria-label="Search students" placeholder="Search student ID" value={query} onChange={(event) => setQuery(event.target.value)} />
        <button type="button" disabled={!selectedBatch}>Upload CSV/Excel</button>
        <button type="button" disabled={!selectedBatch}>Submit</button>
      </div>
      {error ? <p role="alert">{error}</p> : null}
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Student</th><th>Marks</th><th>Moderation</th><th>Remarks</th><th>Recheck Notes</th></tr></thead>
          <tbody>{filteredEntries.map((entry) => <tr key={entry.id}><td>{entry.student_id}</td><td>{entry.marks_obtained}</td><td>{entry.moderation_marks}</td><td>{entry.remarks}</td><td>{entry.recheck_notes}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}
