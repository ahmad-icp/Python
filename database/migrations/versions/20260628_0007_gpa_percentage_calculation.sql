-- GPA & Percentage Calculation module.
CREATE TABLE IF NOT EXISTS grade_systems (
    id VARCHAR(36) PRIMARY KEY,
    college_id VARCHAR(64) NOT NULL,
    name VARCHAR(120) NOT NULL,
    system_type VARCHAR(32) NOT NULL,
    scope_type VARCHAR(40) NOT NULL DEFAULT 'institution',
    scope_id VARCHAR(64) NOT NULL DEFAULT '',
    version INTEGER NOT NULL DEFAULT 1,
    gpa_scale NUMERIC(4,2) NOT NULL DEFAULT 4,
    passing_percentage NUMERIC(5,2) NOT NULL DEFAULT 40,
    passing_gpa NUMERIC(4,2) NOT NULL DEFAULT 2,
    decimal_places INTEGER NOT NULL DEFAULT 2,
    rounding_mode VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_grade_system_scope_version UNIQUE (college_id, scope_type, scope_id, name, version),
    CONSTRAINT ck_grade_system_gpa_scale CHECK (gpa_scale > 0 AND gpa_scale <= 10),
    CONSTRAINT ck_grade_system_passing_percentage CHECK (passing_percentage >= 0 AND passing_percentage <= 100),
    CONSTRAINT ck_grade_system_passing_gpa CHECK (passing_gpa >= 0),
    CONSTRAINT ck_grade_system_decimal_places CHECK (decimal_places >= 0 AND decimal_places <= 4)
);
CREATE INDEX IF NOT EXISTS ix_grade_systems_college_scope_active ON grade_systems (college_id, scope_type, scope_id, is_active);
CREATE TABLE IF NOT EXISTS grade_mappings (
    id VARCHAR(36) PRIMARY KEY,
    college_id VARCHAR(64) NOT NULL,
    system_id VARCHAR(36) NOT NULL REFERENCES grade_systems(id) ON DELETE CASCADE,
    grade VARCHAR(12) NOT NULL,
    min_percentage NUMERIC(5,2) NOT NULL,
    max_percentage NUMERIC(5,2) NOT NULL,
    grade_point NUMERIC(4,2) NOT NULL DEFAULT 0,
    remark VARCHAR(160),
    is_passing BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_grade_mapping_grade UNIQUE (system_id, grade),
    CONSTRAINT ck_grade_mapping_min_pct CHECK (min_percentage >= 0 AND min_percentage <= 100),
    CONSTRAINT ck_grade_mapping_max_pct CHECK (max_percentage >= 0 AND max_percentage <= 100),
    CONSTRAINT ck_grade_mapping_pct_range CHECK (min_percentage <= max_percentage),
    CONSTRAINT ck_grade_mapping_grade_point CHECK (grade_point >= 0)
);
CREATE INDEX IF NOT EXISTS ix_grade_mappings_system_range ON grade_mappings (system_id, min_percentage, max_percentage);
CREATE TABLE IF NOT EXISTS student_grade_calculations (
    id VARCHAR(36) PRIMARY KEY,
    college_id VARCHAR(64) NOT NULL,
    result_id VARCHAR(36) NOT NULL REFERENCES student_results(id) ON DELETE CASCADE,
    exam_id VARCHAR(36) NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    system_id VARCHAR(36) NOT NULL REFERENCES grade_systems(id) ON DELETE RESTRICT,
    percentage NUMERIC(5,2) NOT NULL,
    grade VARCHAR(12) NOT NULL,
    gpa NUMERIC(4,2),
    cgpa NUMERIC(4,2),
    total_credit_hours INTEGER,
    earned_credit_hours INTEGER,
    academic_standing VARCHAR(32) NOT NULL,
    is_promotion_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    calculated_by VARCHAR(64) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    CONSTRAINT uq_grade_calc_result UNIQUE (college_id, result_id),
    CONSTRAINT ck_grade_calc_percentage CHECK (percentage >= 0 AND percentage <= 100),
    CONSTRAINT ck_grade_calc_gpa CHECK (gpa IS NULL OR gpa >= 0),
    CONSTRAINT ck_grade_calc_cgpa CHECK (cgpa IS NULL OR cgpa >= 0)
);
CREATE INDEX IF NOT EXISTS ix_grade_calc_college_student ON student_grade_calculations (college_id, student_id, calculated_at);
CREATE INDEX IF NOT EXISTS ix_grade_calc_college_exam ON student_grade_calculations (college_id, exam_id, percentage);
