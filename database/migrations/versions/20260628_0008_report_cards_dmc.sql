CREATE TABLE IF NOT EXISTS report_cards (
    id VARCHAR(36) PRIMARY KEY,
    college_id VARCHAR(64) NOT NULL,
    result_id VARCHAR(36) NOT NULL REFERENCES student_results(id) ON DELETE CASCADE,
    grade_calculation_id VARCHAR(36) REFERENCES student_grade_calculations(id) ON DELETE SET NULL,
    exam_id VARCHAR(36) NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    verification_code VARCHAR(80) NOT NULL,
    institution_name VARCHAR(180) NOT NULL,
    branding_json TEXT,
    remarks TEXT,
    qr_payload TEXT NOT NULL,
    printable_html TEXT NOT NULL,
    pdf_file_path VARCHAR(500),
    generated_by VARCHAR(64) NOT NULL,
    issued_by VARCHAR(64),
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    issued_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_report_card_result UNIQUE (college_id, result_id),
    CONSTRAINT uq_report_card_verification UNIQUE (college_id, verification_code)
);
CREATE INDEX IF NOT EXISTS ix_report_cards_college_student ON report_cards (college_id, student_id, issued_at);
CREATE INDEX IF NOT EXISTS ix_report_cards_college_exam ON report_cards (college_id, exam_id, status);
