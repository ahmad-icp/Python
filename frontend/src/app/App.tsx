import { AdmissionsPage } from '../features/admissions/AdmissionsPage';
import { StudentPage } from '../features/students/StudentPage';

export function App() {
  return (
    <main style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '2rem' }}>
      <h1>College ERP Platform</h1>
      <p>Multi-tenant ERP foundation for configurable colleges and schools.</p>
      <AdmissionsPage />
      <StudentPage />
    </main>
  );
}
