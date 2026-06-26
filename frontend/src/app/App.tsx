import { AcademicPage } from '../features/academic/AcademicPage';
import { AdmissionsPage } from '../features/admissions/AdmissionsPage';
import { StudentPage } from '../features/students/StudentPage';
import { TimetablePage } from '../features/timetable/TimetablePage';

export function App() {
  return (
    <main style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '2rem' }}>
      <h1>College ERP Platform</h1>
      <p>Multi-tenant ERP foundation for configurable colleges and schools.</p>
      <AcademicPage />
      <AdmissionsPage />
      <TimetablePage />
      <StudentPage />
    </main>
  );
}
