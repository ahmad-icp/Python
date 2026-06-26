import { FormEvent, useEffect, useMemo, useState } from 'react';
import { academicApi, AcademicClass, AcademicSession, Department, Institution, Program, Section, Subject, TeacherAssignment } from '../../services/academic';

export function AcademicPage() {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [sessions, setSessions] = useState<AcademicSession[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [classes, setClasses] = useState<AcademicClass[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [institutionForm, setInstitutionForm] = useState({ name: '', code: '', address: '' });
  const [sessionForm, setSessionForm] = useState({ name: '', start_date: '', end_date: '', status: 'planned' });
  const [departmentForm, setDepartmentForm] = useState({ institution_id: '', name: '', code: '' });
  const [programForm, setProgramForm] = useState({ department_id: '', name: '', code: '', duration_years: 2 });
  const [classForm, setClassForm] = useState({ program_id: '', session_id: '', name: '', display_order: 0 });
  const [sectionForm, setSectionForm] = useState({ class_id: '', name: '', capacity: 40, enrolled_count: 0, room: '' });
  const [subjectForm, setSubjectForm] = useState({ department_id: '', code: '', name: '', credit_hours: 1, weekly_periods: 4, is_elective: false, prerequisite_subject_ids: [] as string[] });
  const [assignmentForm, setAssignmentForm] = useState({ teacher_id: '', teacher_name: '', section_id: '', subject_id: '', weekly_periods: 4, max_weekly_periods: 30 });

  const dashboard = useMemo(() => ({ institutions: institutions.length, sessions: sessions.length, programs: programs.length, classes: classes.length, sections: sections.length, subjects: subjects.length, assignments: assignments.length }), [institutions, sessions, programs, classes, sections, subjects, assignments]);

  async function refresh() {
    const [i, s, d, p, c, sec, sub, a] = await Promise.all([
      academicApi.listInstitutions(search), academicApi.listSessions(), academicApi.listDepartments(), academicApi.listPrograms(), academicApi.listClasses(), academicApi.listSections(), academicApi.listSubjects(), academicApi.listTeacherAssignments(),
    ]);
    setInstitutions(i.items); setSessions(s.items); setDepartments(d.items); setPrograms(p.items); setClasses(c.items); setSections(sec.items); setSubjects(sub.items); setAssignments(a.items);
  }

  useEffect(() => { refresh().catch((loadError: Error) => setError(loadError.message)); }, []);

  async function submit<T>(event: FormEvent, action: () => Promise<T>, message: string) {
    event.preventDefault(); setError(null); setSuccess(null);
    try { await action(); setSuccess(message); await refresh(); } catch (submitError) { setError(submitError instanceof Error ? submitError.message : 'Academic action failed'); }
  }

  return <section>
    <h2>Academic Management</h2>
    <p>Manage institution structure, sessions, programs, classes, sections, subjects, allocations, and teacher workload from one academic control center.</p>
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>{Object.entries(dashboard).map(([key, value]) => <strong key={key}>{key}: {value}</strong>)}</div>
    <label>Search institutions <input value={search} onChange={(event) => setSearch(event.target.value)} onBlur={() => refresh().catch((loadError: Error) => setError(loadError.message))} /></label>
    {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}{success && <p role="status" style={{ color: 'green' }}>{success}</p>}

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
      <form onSubmit={(e) => submit(e, () => academicApi.createInstitution(institutionForm), 'Institution saved.')}><h3>Institution</h3><input aria-label="Institution name" placeholder="Name" value={institutionForm.name} onChange={(e) => setInstitutionForm({ ...institutionForm, name: e.target.value })} /><input aria-label="Institution code" placeholder="Code" value={institutionForm.code} onChange={(e) => setInstitutionForm({ ...institutionForm, code: e.target.value })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createSession(sessionForm), 'Session saved.')}><h3>Session</h3><input aria-label="Session name" placeholder="2026-2027" value={sessionForm.name} onChange={(e) => setSessionForm({ ...sessionForm, name: e.target.value })} /><input aria-label="Session start" type="date" value={sessionForm.start_date} onChange={(e) => setSessionForm({ ...sessionForm, start_date: e.target.value })} /><input aria-label="Session end" type="date" value={sessionForm.end_date} onChange={(e) => setSessionForm({ ...sessionForm, end_date: e.target.value })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createDepartment(departmentForm), 'Department saved.')}><h3>Department</h3><select value={departmentForm.institution_id} onChange={(e) => setDepartmentForm({ ...departmentForm, institution_id: e.target.value })}><option value="">Institution</option>{institutions.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}</select><input placeholder="Name" value={departmentForm.name} onChange={(e) => setDepartmentForm({ ...departmentForm, name: e.target.value })} /><input placeholder="Code" value={departmentForm.code} onChange={(e) => setDepartmentForm({ ...departmentForm, code: e.target.value })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createProgram(programForm), 'Program saved.')}><h3>Program</h3><select value={programForm.department_id} onChange={(e) => setProgramForm({ ...programForm, department_id: e.target.value })}><option value="">Department</option>{departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}</select><input placeholder="Name" value={programForm.name} onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} /><input placeholder="Code" value={programForm.code} onChange={(e) => setProgramForm({ ...programForm, code: e.target.value })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createClass(classForm), 'Class saved.')}><h3>Class</h3><select value={classForm.program_id} onChange={(e) => setClassForm({ ...classForm, program_id: e.target.value })}><option value="">Program</option>{programs.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select><select value={classForm.session_id} onChange={(e) => setClassForm({ ...classForm, session_id: e.target.value })}><option value="">Session</option>{sessions.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select><input placeholder="Class name" value={classForm.name} onChange={(e) => setClassForm({ ...classForm, name: e.target.value })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createSection(sectionForm), 'Section saved.')}><h3>Section</h3><select value={sectionForm.class_id} onChange={(e) => setSectionForm({ ...sectionForm, class_id: e.target.value })}><option value="">Class</option>{classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select><input placeholder="Section" value={sectionForm.name} onChange={(e) => setSectionForm({ ...sectionForm, name: e.target.value })} /><input type="number" value={sectionForm.capacity} onChange={(e) => setSectionForm({ ...sectionForm, capacity: Number(e.target.value) })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createSubject({ ...subjectForm, department_id: subjectForm.department_id || undefined }), 'Subject saved.')}><h3>Subject</h3><input placeholder="Code" value={subjectForm.code} onChange={(e) => setSubjectForm({ ...subjectForm, code: e.target.value })} /><input placeholder="Name" value={subjectForm.name} onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })} /><input type="number" value={subjectForm.weekly_periods} onChange={(e) => setSubjectForm({ ...subjectForm, weekly_periods: Number(e.target.value) })} /><button>Create</button></form>
      <form onSubmit={(e) => submit(e, () => academicApi.createTeacherAssignment(assignmentForm), 'Teacher assigned.')}><h3>Teacher Assignment</h3><input placeholder="Teacher ID" value={assignmentForm.teacher_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, teacher_id: e.target.value })} /><input placeholder="Teacher name" value={assignmentForm.teacher_name} onChange={(e) => setAssignmentForm({ ...assignmentForm, teacher_name: e.target.value })} /><select value={assignmentForm.section_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, section_id: e.target.value })}><option value="">Section</option>{sections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select><select value={assignmentForm.subject_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, subject_id: e.target.value })}><option value="">Subject</option>{subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select><button>Assign</button></form>
    </div>
  </section>;
}
