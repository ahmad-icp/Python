import { FormEvent, useEffect, useMemo, useState } from 'react';

import { createStudent, listStudents, Student, StudentForm } from '../../services/students';

const emptyStudent: StudentForm = {
  admission_number: '',
  roll_number: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: 'female',
  email: '',
  mobile: '',
  address: '',
  program: '',
  current_class: '',
  current_section: '',
  academic_session: '',
  enrollment_date: '',
  guardians: [
    {
      full_name: '',
      relationship: 'father',
      mobile: '',
      email: '',
      occupation: '',
      is_primary: true,
    },
  ],
};

function validateStudent(form: StudentForm): string[] {
  const errors: string[] = [];
  if (!form.admission_number.trim()) errors.push('Admission number is required.');
  if (form.first_name.trim().length < 2) errors.push('First name must contain at least two characters.');
  if (!form.last_name.trim()) errors.push('Last name is required.');
  if (!form.date_of_birth) errors.push('Date of birth is required.');
  if (form.address.trim().length < 5) errors.push('Address must contain at least five characters.');
  if (!form.program.trim()) errors.push('Program is required.');
  if (!form.current_class.trim()) errors.push('Class is required.');
  if (!form.academic_session.trim()) errors.push('Academic session is required.');
  if (!form.enrollment_date) errors.push('Enrollment date is required.');
  const primaryGuardians = form.guardians.filter((guardian) => guardian.is_primary);
  if (primaryGuardians.length !== 1) errors.push('Exactly one primary guardian is required.');
  if (!form.guardians[0]?.full_name.trim()) errors.push('Primary guardian name is required.');
  if ((form.guardians[0]?.mobile ?? '').trim().length < 7) errors.push('Primary guardian mobile is required.');
  return errors;
}

export function StudentPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [form, setForm] = useState<StudentForm>(emptyStudent);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const validationErrors = useMemo(() => validateStudent(form), [form]);

  async function refreshStudents() {
    const response = await listStudents();
    setStudents(response.items);
  }

  useEffect(() => {
    refreshStudents().catch((loadError: Error) => setError(loadError.message));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (validationErrors.length > 0) {
      setError(validationErrors.join(' '));
      return;
    }
    setLoading(true);
    try {
      await createStudent(form);
      setForm(emptyStudent);
      setSuccess('Student profile created successfully.');
      await refreshStudents();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to create student');
    } finally {
      setLoading(false);
    }
  }

  function updateField(field: keyof StudentForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateGuardian(field: keyof StudentForm['guardians'][number], value: string) {
    setForm((current) => ({
      ...current,
      guardians: [{ ...current.guardians[0], [field]: value }],
    }));
  }

  return (
    <section>
      <h2>Student Information System</h2>
      <p>Create student profiles, attach guardian data, track status, and prepare records for promotion or alumni workflows.</p>

      <form onSubmit={handleSubmit} aria-label="Create student profile">
        <fieldset disabled={loading} style={{ display: 'grid', gap: '0.75rem', maxWidth: '760px' }}>
          <legend>Student Profile</legend>
          <input aria-label="Admission number" placeholder="Admission number" value={form.admission_number} onChange={(event) => updateField('admission_number', event.target.value)} />
          <input aria-label="Roll number" placeholder="Roll number" value={form.roll_number} onChange={(event) => updateField('roll_number', event.target.value)} />
          <input aria-label="First name" placeholder="First name" value={form.first_name} onChange={(event) => updateField('first_name', event.target.value)} />
          <input aria-label="Last name" placeholder="Last name" value={form.last_name} onChange={(event) => updateField('last_name', event.target.value)} />
          <input aria-label="Date of birth" type="date" value={form.date_of_birth} onChange={(event) => updateField('date_of_birth', event.target.value)} />
          <select aria-label="Gender" value={form.gender} onChange={(event) => updateField('gender', event.target.value)}>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
          <input aria-label="Program" placeholder="Program" value={form.program} onChange={(event) => updateField('program', event.target.value)} />
          <input aria-label="Class" placeholder="Class" value={form.current_class} onChange={(event) => updateField('current_class', event.target.value)} />
          <input aria-label="Section" placeholder="Section" value={form.current_section} onChange={(event) => updateField('current_section', event.target.value)} />
          <input aria-label="Academic session" placeholder="Academic session" value={form.academic_session} onChange={(event) => updateField('academic_session', event.target.value)} />
          <input aria-label="Enrollment date" type="date" value={form.enrollment_date} onChange={(event) => updateField('enrollment_date', event.target.value)} />
          <textarea aria-label="Address" placeholder="Address" value={form.address} onChange={(event) => updateField('address', event.target.value)} />
        </fieldset>

        <fieldset disabled={loading} style={{ display: 'grid', gap: '0.75rem', maxWidth: '760px', marginTop: '1rem' }}>
          <legend>Primary Guardian</legend>
          <input aria-label="Guardian full name" placeholder="Guardian full name" value={form.guardians[0].full_name} onChange={(event) => updateGuardian('full_name', event.target.value)} />
          <select aria-label="Guardian relationship" value={form.guardians[0].relationship} onChange={(event) => updateGuardian('relationship', event.target.value)}>
            <option value="father">Father</option>
            <option value="mother">Mother</option>
            <option value="guardian">Guardian</option>
            <option value="other">Other</option>
          </select>
          <input aria-label="Guardian mobile" placeholder="Guardian mobile" value={form.guardians[0].mobile} onChange={(event) => updateGuardian('mobile', event.target.value)} />
        </fieldset>

        {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
        {success && <p role="status" style={{ color: 'green' }}>{success}</p>}
        <button type="submit" disabled={loading || validationErrors.length > 0}>Create Student</button>
      </form>

      <h3>Student Records</h3>
      <table>
        <thead>
          <tr>
            <th>Admission #</th>
            <th>Name</th>
            <th>Class</th>
            <th>Session</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>{student.admission_number}</td>
              <td>{student.first_name} {student.last_name}</td>
              <td>{student.current_class}{student.current_section ? `-${student.current_section}` : ''}</td>
              <td>{student.academic_session}</td>
              <td>{student.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
