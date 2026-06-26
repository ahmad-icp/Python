import { FormEvent, useEffect, useMemo, useState } from 'react';

import {
  AdmissionApplication,
  AdmissionApplicationForm,
  createAdmissionApplication,
  createMeritList,
  listAdmissionApplications,
  markApplicationEligible,
  MeritListRequest,
} from '../../services/admissions';

const emptyApplication: AdmissionApplicationForm = {
  application_number: '',
  mode: 'online',
  applicant_first_name: '',
  applicant_last_name: '',
  date_of_birth: '',
  gender: 'female',
  email: '',
  mobile: '',
  address: '',
  guardian_name: '',
  guardian_mobile: '',
  guardian_email: '',
  previous_school: '',
  previous_class: '',
  program: '',
  applying_for_class: '',
  preferred_section: '',
  academic_session: '',
  obtained_marks: undefined,
  total_marks: undefined,
  documents: [],
};

const emptyMeritList: MeritListRequest = {
  title: '',
  program: '',
  academic_session: '',
  list_number: 1,
  capacity: 25,
  minimum_score: 0,
  offer_expires_on: '',
};

function validateApplication(form: AdmissionApplicationForm): string[] {
  const errors: string[] = [];
  if (!form.application_number.trim()) errors.push('Application number is required.');
  if (form.applicant_first_name.trim().length < 2) errors.push('Applicant first name must contain at least two characters.');
  if (!form.applicant_last_name.trim()) errors.push('Applicant last name is required.');
  if (!form.date_of_birth) errors.push('Date of birth is required.');
  if (form.address.trim().length < 5) errors.push('Address must contain at least five characters.');
  if (form.guardian_name.trim().length < 2) errors.push('Guardian name is required.');
  if (form.guardian_mobile.trim().length < 7) errors.push('Guardian mobile is required.');
  if (!form.program.trim()) errors.push('Program is required.');
  if (!form.applying_for_class.trim()) errors.push('Applying class is required.');
  if (!form.academic_session.trim()) errors.push('Academic session is required.');
  if ((form.obtained_marks === undefined) !== (form.total_marks === undefined)) errors.push('Obtained and total marks must be entered together.');
  if (form.obtained_marks !== undefined && form.total_marks !== undefined && form.obtained_marks > form.total_marks) errors.push('Obtained marks cannot exceed total marks.');
  return errors;
}

export function AdmissionsPage() {
  const [applications, setApplications] = useState<AdmissionApplication[]>([]);
  const [applicationForm, setApplicationForm] = useState<AdmissionApplicationForm>(emptyApplication);
  const [meritListForm, setMeritListForm] = useState<MeritListRequest>(emptyMeritList);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const validationErrors = useMemo(() => validateApplication(applicationForm), [applicationForm]);

  async function refreshApplications() {
    const response = await listAdmissionApplications();
    setApplications(response.items);
  }

  useEffect(() => {
    refreshApplications().catch((loadError: Error) => setError(loadError.message));
  }, []);

  function updateApplicationField(field: keyof AdmissionApplicationForm, value: string) {
    const numericFields = new Set<keyof AdmissionApplicationForm>(['obtained_marks', 'total_marks']);
    setApplicationForm((current) => ({
      ...current,
      [field]: numericFields.has(field) && value !== '' ? Number(value) : value || undefined,
    }));
  }

  async function handleApplicationSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (validationErrors.length > 0) {
      setError(validationErrors.join(' '));
      return;
    }
    setLoading(true);
    try {
      await createAdmissionApplication(applicationForm);
      setApplicationForm(emptyApplication);
      setSuccess('Admission application submitted successfully.');
      await refreshApplications();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to submit admission application');
    } finally {
      setLoading(false);
    }
  }

  async function handleEligible(applicationId: string) {
    setError(null);
    setSuccess(null);
    try {
      await markApplicationEligible(applicationId);
      setSuccess('Application marked eligible.');
      await refreshApplications();
    } catch (decisionError) {
      setError(decisionError instanceof Error ? decisionError.message : 'Unable to update application');
    }
  }

  async function handleMeritListSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const meritList = await createMeritList(meritListForm);
      setSuccess(`Merit list created with ${meritList.entries.length} applicant(s).`);
      setMeritListForm(emptyMeritList);
      await refreshApplications();
    } catch (meritError) {
      setError(meritError instanceof Error ? meritError.message : 'Unable to create merit list');
    }
  }

  return (
    <section>
      <h2>Admissions Management</h2>
      <p>Capture online/offline applications, validate applicant data, review eligibility, and prepare merit lists.</p>

      <form onSubmit={handleApplicationSubmit} aria-label="Create admission application">
        <fieldset disabled={loading} style={{ display: 'grid', gap: '0.75rem', maxWidth: '760px' }}>
          <legend>Application</legend>
          <input aria-label="Application number" placeholder="Application number" value={applicationForm.application_number} onChange={(event) => updateApplicationField('application_number', event.target.value)} />
          <select aria-label="Application mode" value={applicationForm.mode} onChange={(event) => updateApplicationField('mode', event.target.value)}>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
          </select>
          <input aria-label="Applicant first name" placeholder="Applicant first name" value={applicationForm.applicant_first_name} onChange={(event) => updateApplicationField('applicant_first_name', event.target.value)} />
          <input aria-label="Applicant last name" placeholder="Applicant last name" value={applicationForm.applicant_last_name} onChange={(event) => updateApplicationField('applicant_last_name', event.target.value)} />
          <input aria-label="Applicant date of birth" type="date" value={applicationForm.date_of_birth} onChange={(event) => updateApplicationField('date_of_birth', event.target.value)} />
          <select aria-label="Applicant gender" value={applicationForm.gender} onChange={(event) => updateApplicationField('gender', event.target.value)}>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
          <textarea aria-label="Applicant address" placeholder="Address" value={applicationForm.address} onChange={(event) => updateApplicationField('address', event.target.value)} />
          <input aria-label="Guardian name" placeholder="Guardian name" value={applicationForm.guardian_name} onChange={(event) => updateApplicationField('guardian_name', event.target.value)} />
          <input aria-label="Guardian mobile" placeholder="Guardian mobile" value={applicationForm.guardian_mobile} onChange={(event) => updateApplicationField('guardian_mobile', event.target.value)} />
          <input aria-label="Program" placeholder="Program" value={applicationForm.program} onChange={(event) => updateApplicationField('program', event.target.value)} />
          <input aria-label="Applying for class" placeholder="Applying for class" value={applicationForm.applying_for_class} onChange={(event) => updateApplicationField('applying_for_class', event.target.value)} />
          <input aria-label="Preferred section" placeholder="Preferred section" value={applicationForm.preferred_section} onChange={(event) => updateApplicationField('preferred_section', event.target.value)} />
          <input aria-label="Academic session" placeholder="Academic session" value={applicationForm.academic_session} onChange={(event) => updateApplicationField('academic_session', event.target.value)} />
          <input aria-label="Obtained marks" type="number" placeholder="Obtained marks" value={applicationForm.obtained_marks ?? ''} onChange={(event) => updateApplicationField('obtained_marks', event.target.value)} />
          <input aria-label="Total marks" type="number" placeholder="Total marks" value={applicationForm.total_marks ?? ''} onChange={(event) => updateApplicationField('total_marks', event.target.value)} />
        </fieldset>
        <button type="submit" disabled={loading || validationErrors.length > 0}>Submit Application</button>
      </form>

      <form onSubmit={handleMeritListSubmit} aria-label="Create merit list" style={{ marginTop: '1.5rem' }}>
        <fieldset style={{ display: 'grid', gap: '0.75rem', maxWidth: '760px' }}>
          <legend>Merit List</legend>
          <input aria-label="Merit list title" placeholder="Merit list title" value={meritListForm.title} onChange={(event) => setMeritListForm((current) => ({ ...current, title: event.target.value }))} />
          <input aria-label="Merit list program" placeholder="Program" value={meritListForm.program} onChange={(event) => setMeritListForm((current) => ({ ...current, program: event.target.value }))} />
          <input aria-label="Merit list session" placeholder="Academic session" value={meritListForm.academic_session} onChange={(event) => setMeritListForm((current) => ({ ...current, academic_session: event.target.value }))} />
          <input aria-label="Merit list capacity" type="number" placeholder="Capacity" value={meritListForm.capacity} onChange={(event) => setMeritListForm((current) => ({ ...current, capacity: Number(event.target.value) }))} />
          <input aria-label="Minimum score" type="number" placeholder="Minimum score" value={meritListForm.minimum_score ?? ''} onChange={(event) => setMeritListForm((current) => ({ ...current, minimum_score: Number(event.target.value) }))} />
        </fieldset>
        <button type="submit">Create Merit List</button>
      </form>

      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
      {success && <p role="status" style={{ color: 'green' }}>{success}</p>}

      <h3>Applications</h3>
      <table>
        <thead>
          <tr>
            <th>Application #</th>
            <th>Applicant</th>
            <th>Program</th>
            <th>Class</th>
            <th>Merit</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td>{application.application_number}</td>
              <td>{application.applicant_first_name} {application.applicant_last_name}</td>
              <td>{application.program}</td>
              <td>{application.applying_for_class}</td>
              <td>{application.merit_score ?? 'N/A'}</td>
              <td>{application.status}</td>
              <td>
                <button type="button" onClick={() => handleEligible(application.id)} disabled={application.status === 'admitted'}>Mark Eligible</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
