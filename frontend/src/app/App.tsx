import { AcademicPage } from '../features/academic/AcademicPage';
import { AdmissionsPage } from '../features/admissions/AdmissionsPage';
import { AttendancePage } from '../features/attendance/AttendancePage';
import { ExaminationPage } from '../features/examinations/ExaminationPage';
import { MarksEntryPage } from '../features/marks-entry/MarksEntryPage';
import { ResultProcessingPage } from '../features/results/ResultProcessingPage';
import { GradeCalculationPage } from '../features/grade-calculations/GradeCalculationPage';
import { ReportCardsPage } from '../features/report-cards/ReportCardsPage';
import { MeritListsPage } from '../features/merit-lists/MeritListsPage';
import { TranscriptsPage } from '../features/transcripts/TranscriptsPage';
import { FinancePage } from '../features/fees/FinancePage';
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
      <AttendancePage />
      <ExaminationPage />
      <MarksEntryPage />
      <ResultProcessingPage />
      <GradeCalculationPage />
      <ReportCardsPage />
      <MeritListsPage />
      <TranscriptsPage />
      <StudentPage />
      <FinancePage />
    </main>
  );
}
