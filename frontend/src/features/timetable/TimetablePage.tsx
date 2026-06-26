import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Classroom, TimeSlot, TimetableEntry, TimetableVersion, timetableApi } from '../../services/timetable';

const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function TimetablePage() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [versions, setVersions] = useState<TimetableVersion[]>([]);
  const [entries, setEntries] = useState<TimetableEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [roomForm, setRoomForm] = useState({ name: '', code: '', room_type: 'classroom', capacity: 40 });
  const [slotForm, setSlotForm] = useState({ name: '', start_time: '08:00', end_time: '08:45', sort_order: 1, is_break: false });
  const [versionForm, setVersionForm] = useState({ session_id: '', section_id: '', effective_from: '', effective_to: '' });
  const [entryForm, setEntryForm] = useState({ version_id: '', subject_id: '', teacher_id: '', teacher_name: '', classroom_id: '', time_slot_id: '', weekday: 1, entry_type: 'lecture' });
  const [filterTeacher, setFilterTeacher] = useState('');

  async function refresh() {
    const [rooms, slots, versionPage, entryPage] = await Promise.all([timetableApi.listClassrooms(), timetableApi.listTimeSlots(), timetableApi.listVersions(), timetableApi.listEntries()]);
    setClassrooms(rooms.items); setTimeSlots(slots.items); setVersions(versionPage.items); setEntries(entryPage.items);
  }

  useEffect(() => { refresh().catch((loadError: Error) => setError(loadError.message)); }, []);

  async function submit<T>(event: FormEvent, action: () => Promise<T>, message: string) {
    event.preventDefault(); setError(null); setSuccess(null);
    try { await action(); setSuccess(message); await refresh(); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : 'Timetable action failed'); }
  }

  const visibleEntries = useMemo(() => entries.filter((entry) => !filterTeacher || entry.teacher_name.toLowerCase().includes(filterTeacher.toLowerCase()) || entry.teacher_id.includes(filterTeacher)), [entries, filterTeacher]);

  return <section>
    <h2>Timetable Management</h2>
    <p>Build versioned weekly timetables with teacher, classroom, section, room-capacity, workload, and holiday validation.</p>
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}><strong>Rooms: {classrooms.length}</strong><strong>Slots: {timeSlots.length}</strong><strong>Versions: {versions.length}</strong><strong>Entries: {entries.length}</strong></div>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}{success && <p role="status" style={{ color: 'green' }}>{success}</p>}

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
      <form onSubmit={(e) => submit(e, () => timetableApi.createClassroom(roomForm), 'Classroom saved.')}><h3>Classroom/Lab</h3><input placeholder="Room name" value={roomForm.name} onChange={(e) => setRoomForm({ ...roomForm, name: e.target.value })} /><input placeholder="Code" value={roomForm.code} onChange={(e) => setRoomForm({ ...roomForm, code: e.target.value })} /><select value={roomForm.room_type} onChange={(e) => setRoomForm({ ...roomForm, room_type: e.target.value })}><option value="classroom">Classroom</option><option value="lab">Lab</option><option value="auditorium">Auditorium</option></select><input type="number" value={roomForm.capacity} onChange={(e) => setRoomForm({ ...roomForm, capacity: Number(e.target.value) })} /><button>Create Room</button></form>
      <form onSubmit={(e) => submit(e, () => timetableApi.createTimeSlot(slotForm), 'Time slot saved.')}><h3>Time Slot</h3><input placeholder="Slot name" value={slotForm.name} onChange={(e) => setSlotForm({ ...slotForm, name: e.target.value })} /><input type="time" value={slotForm.start_time} onChange={(e) => setSlotForm({ ...slotForm, start_time: e.target.value })} /><input type="time" value={slotForm.end_time} onChange={(e) => setSlotForm({ ...slotForm, end_time: e.target.value })} /><label><input type="checkbox" checked={slotForm.is_break} onChange={(e) => setSlotForm({ ...slotForm, is_break: e.target.checked })} /> Break</label><button>Create Slot</button></form>
      <form onSubmit={(e) => submit(e, () => timetableApi.createVersion(versionForm), 'Timetable version created.')}><h3>Version</h3><input placeholder="Academic session ID" value={versionForm.session_id} onChange={(e) => setVersionForm({ ...versionForm, session_id: e.target.value })} /><input placeholder="Section ID" value={versionForm.section_id} onChange={(e) => setVersionForm({ ...versionForm, section_id: e.target.value })} /><input type="date" value={versionForm.effective_from} onChange={(e) => setVersionForm({ ...versionForm, effective_from: e.target.value })} /><input type="date" value={versionForm.effective_to} onChange={(e) => setVersionForm({ ...versionForm, effective_to: e.target.value })} /><button>Create Version</button></form>
      <form onSubmit={(e) => submit(e, () => timetableApi.createEntry(entryForm), 'Lecture scheduled.')}><h3>Manual Editor</h3><select value={entryForm.version_id} onChange={(e) => setEntryForm({ ...entryForm, version_id: e.target.value })}><option value="">Version</option>{versions.map(v => <option key={v.id} value={v.id}>Section {v.section_id} v{v.version_number}</option>)}</select><input placeholder="Subject ID" value={entryForm.subject_id} onChange={(e) => setEntryForm({ ...entryForm, subject_id: e.target.value })} /><input placeholder="Teacher ID" value={entryForm.teacher_id} onChange={(e) => setEntryForm({ ...entryForm, teacher_id: e.target.value })} /><input placeholder="Teacher name" value={entryForm.teacher_name} onChange={(e) => setEntryForm({ ...entryForm, teacher_name: e.target.value })} /><select value={entryForm.classroom_id} onChange={(e) => setEntryForm({ ...entryForm, classroom_id: e.target.value })}><option value="">Room</option>{classrooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select><select value={entryForm.time_slot_id} onChange={(e) => setEntryForm({ ...entryForm, time_slot_id: e.target.value })}><option value="">Slot</option>{timeSlots.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select><select value={entryForm.weekday} onChange={(e) => setEntryForm({ ...entryForm, weekday: Number(e.target.value) })}>{weekdays.map((day, index) => <option key={day} value={index + 1}>{day}</option>)}</select><button>Schedule</button></form>
    </div>

    <h3>Weekly Calendar</h3><label>Teacher/Classroom/Student filter <input value={filterTeacher} onChange={(e) => setFilterTeacher(e.target.value)} /></label>
    <div style={{ overflowX: 'auto' }}><table><thead><tr><th>Slot</th>{weekdays.map(day => <th key={day}>{day}</th>)}</tr></thead><tbody>{timeSlots.map(slot => <tr key={slot.id}><th>{slot.name}</th>{weekdays.map((day, dayIndex) => { const entry = visibleEntries.find(item => item.time_slot_id === slot.id && item.weekday === dayIndex + 1); return <td key={day}>{entry ? <span>{entry.teacher_name}<br />Subject: {entry.subject_id}<br />Room: {entry.classroom_id}</span> : '-'}</td>; })}</tr>)}</tbody></table></div>
    <button type="button" onClick={() => window.print()}>Print / Save as PDF</button>
  </section>;
}
