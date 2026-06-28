-- Result Processing module: grading policies, calculated student results, subject results, and audit trail.
CREATE TABLE IF NOT EXISTS grading_policies (
    id VARCHAR(36) PRIMARY KEY,
    college_id VARCHAR(64) NOT NULL,
    name VARCHAR(120) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    minimum_percentage NUMERIC(5,2) NOT NULL DEFAULT 40,
    grace_marks NUMERIC(7,2) NOT NULL DEFAULT 0,
    promotion_minimum_percentage NUMERIC(5,2) NOT NULL DEFAULT 40,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_grading_policy_name_version UNIQUE (college_id, name, version),
    CONSTRAINT ck_policy_min_percentage CHECK (minimum_percentage >= 0 AND minimum_percentage <= 100),
    CONSTRAINT ck_policy_grace_non_negative CHECK (grace_marks >= 0),
    CONSTRAINT ck_policy_promotion_percentage CHECK (promotion_minimum_percentage >= 0 AND promotion_minimum_percentage <= 100)
);
CREATE INDEX IF NOT EXISTS ix_grading_policies_college_active ON grading_policies (college_id, is_active);
CREATE TABLE IF NOT EXISTS student_results (
    id VARCHAR(36) PRIMARY KEY, college_id VARCHAR(64) NOT NULL, exam_id VARCHAR(36) NOT NULL REFERENCES exams(id) ON DELETE CASCADE, student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE, policy_id VARCHAR(36) REFERENCES grading_policies(id) ON DELETE SET NULL, status VARCHAR(32) NOT NULL DEFAULT 'DRAFT', outcome VARCHAR(32) NOT NULL DEFAULT 'INCOMPLETE', total_marks NUMERIC(9,2) NOT NULL DEFAULT 0, obtained_marks NUMERIC(9,2) NOT NULL DEFAULT 0, grace_awarded NUMERIC(7,2) NOT NULL DEFAULT 0, percentage NUMERIC(5,2) NOT NULL DEFAULT 0, is_promotion_eligible BOOLEAN NOT NULL DEFAULT FALSE, calculated_by VARCHAR(64) NOT NULL, calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, published_by VARCHAR(64), published_at TIMESTAMP WITH TIME ZONE, locked_by VARCHAR(64), locked_at TIMESTAMP WITH TIME ZONE, CONSTRAINT uq_student_result_exam UNIQUE (college_id, exam_id, student_id), CONSTRAINT ck_result_marks_non_negative CHECK (total_marks >= 0 AND obtained_marks >= 0), CONSTRAINT ck_result_percentage_range CHECK (percentage >= 0 AND percentage <= 100)
);
CREATE INDEX IF NOT EXISTS ix_results_college_exam_status ON student_results (college_id, exam_id, status);
CREATE INDEX IF NOT EXISTS ix_results_college_student_exam ON student_results (college_id, student_id, exam_id);
CREATE TABLE IF NOT EXISTS subject_results (
    id VARCHAR(36) PRIMARY KEY, college_id VARCHAR(64) NOT NULL, result_id VARCHAR(36) NOT NULL REFERENCES student_results(id) ON DELETE CASCADE, exam_id VARCHAR(36) NOT NULL REFERENCES exams(id) ON DELETE CASCADE, student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE, subject_id VARCHAR(36) NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT, credit_hours INTEGER NOT NULL DEFAULT 1, maximum_marks NUMERIC(9,2) NOT NULL, obtained_marks NUMERIC(9,2) NOT NULL, grace_awarded NUMERIC(7,2) NOT NULL DEFAULT 0, percentage NUMERIC(5,2) NOT NULL, outcome VARCHAR(32) NOT NULL, remarks TEXT, CONSTRAINT uq_subject_result_per_result UNIQUE (result_id, subject_id)
);
CREATE INDEX IF NOT EXISTS ix_subject_results_college_exam_subject ON subject_results (college_id, exam_id, subject_id);
CREATE TABLE IF NOT EXISTS result_audit_trails (id VARCHAR(36) PRIMARY KEY, college_id VARCHAR(64) NOT NULL, result_id VARCHAR(36) REFERENCES student_results(id) ON DELETE SET NULL, action VARCHAR(32) NOT NULL, actor_id VARCHAR(64) NOT NULL, details TEXT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS ix_result_audit_college_result_created ON result_audit_trails (college_id, result_id, created_at);
