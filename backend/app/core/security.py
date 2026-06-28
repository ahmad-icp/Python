from enum import StrEnum

from fastapi import Depends, Header, HTTPException, status


class Permission(StrEnum):
    STUDENT_READ = "student:read"
    STUDENT_WRITE = "student:write"
    STUDENT_DELETE = "student:delete"
    STUDENT_PROMOTE = "student:promote"
    STUDENT_ALUMNI = "student:alumni"
    DOCUMENT_VERIFY = "document:verify"
    ADMISSION_READ = "admission:read"
    ADMISSION_WRITE = "admission:write"
    ADMISSION_DECIDE = "admission:decide"
    ADMISSION_ENROLL = "admission:enroll"
    MERIT_LIST_MANAGE = "merit_list:manage"
    ACADEMIC_READ = "academic:read"
    ACADEMIC_WRITE = "academic:write"
    ACADEMIC_ASSIGN = "academic:assign"
    ACADEMIC_DELETE = "academic:delete"
    TIMETABLE_READ = "timetable:read"
    TIMETABLE_WRITE = "timetable:write"
    TIMETABLE_PUBLISH = "timetable:publish"
    TIMETABLE_DELETE = "timetable:delete"
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"
    ATTENDANCE_MARK = "attendance:mark"
    ATTENDANCE_FINALIZE = "attendance:finalize"
    EXAM_READ = "exam:read"
    EXAM_WRITE = "exam:write"
    EXAM_CONFIGURE = "exam:configure"
    EXAM_SCHEDULE = "exam:schedule"
    EXAM_PUBLISH = "exam:publish"
    EXAM_LOCK = "exam:lock"
    MARKS_READ = "marks:read"
    MARKS_WRITE = "marks:write"
    MARKS_SUBMIT = "marks:submit"
    MARKS_LOCK = "marks:lock"
    RESULT_READ = "result:read"
    RESULT_CALCULATE = "result:calculate"
    RESULT_CONFIGURE = "result:configure"
    RESULT_PUBLISH = "result:publish"
    RESULT_LOCK = "result:lock"
    GRADE_READ = "grade:read"
    GRADE_CONFIGURE = "grade:configure"
    GRADE_CALCULATE = "grade:calculate"
    REPORT_CARD_READ = "report_card:read"
    REPORT_CARD_WRITE = "report_card:write"
    REPORT_CARD_ISSUE = "report_card:issue"
    GAZETTE_READ = "gazette:read"
    GAZETTE_WRITE = "gazette:write"
    MERIT_READ = "merit:read"
    MERIT_WRITE = "merit:write"
    MERIT_PUBLISH = "merit:publish"
    TRANSCRIPT_READ = "transcript:read"
    TRANSCRIPT_WRITE = "transcript:write"
    TRANSCRIPT_ISSUE = "transcript:issue"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "platform_super_admin": set(Permission),
    "college_owner": set(Permission),
    "principal": set(Permission),
    "administrator": set(Permission),
    "admission_officer": {
        Permission.STUDENT_READ,
        Permission.STUDENT_WRITE,
        Permission.DOCUMENT_VERIFY,
        Permission.ADMISSION_READ,
        Permission.ADMISSION_WRITE,
        Permission.ADMISSION_DECIDE,
        Permission.ADMISSION_ENROLL,
        Permission.MERIT_LIST_MANAGE,
        Permission.ACADEMIC_READ,
        Permission.TIMETABLE_READ,
        Permission.ATTENDANCE_READ,
        Permission.EXAM_READ,
        Permission.MARKS_READ, Permission.RESULT_READ, Permission.GRADE_READ, Permission.REPORT_CARD_READ, Permission.GAZETTE_READ, Permission.MERIT_READ, Permission.TRANSCRIPT_READ,
    },
    "teacher": {Permission.STUDENT_READ, Permission.ACADEMIC_READ, Permission.TIMETABLE_READ, Permission.ATTENDANCE_READ, Permission.ATTENDANCE_MARK, Permission.EXAM_READ, Permission.MARKS_READ, Permission.MARKS_WRITE, Permission.MARKS_SUBMIT, Permission.RESULT_READ, Permission.GRADE_READ, Permission.REPORT_CARD_READ, Permission.GAZETTE_READ, Permission.MERIT_READ, Permission.TRANSCRIPT_READ},
    "parent": {Permission.STUDENT_READ, Permission.ACADEMIC_READ, Permission.TIMETABLE_READ, Permission.ATTENDANCE_READ, Permission.EXAM_READ, Permission.MARKS_READ, Permission.RESULT_READ, Permission.GRADE_READ, Permission.REPORT_CARD_READ, Permission.GAZETTE_READ, Permission.MERIT_READ, Permission.TRANSCRIPT_READ},
    "student": {Permission.STUDENT_READ, Permission.ACADEMIC_READ, Permission.TIMETABLE_READ, Permission.ATTENDANCE_READ, Permission.EXAM_READ, Permission.MARKS_READ, Permission.RESULT_READ, Permission.GRADE_READ, Permission.REPORT_CARD_READ, Permission.GAZETTE_READ, Permission.MERIT_READ, Permission.TRANSCRIPT_READ},
}


class CurrentUser:
    def __init__(self, user_id: str, college_id: str, role: str) -> None:
        self.user_id = user_id
        self.college_id = college_id
        self.role = role
        self.permissions = ROLE_PERMISSIONS.get(role, set())


def get_current_user(
    x_user_id: str = Header(default="development-user"),
    x_college_id: str = Header(default="college-demo"),
    x_role: str = Header(default="administrator"),
) -> CurrentUser:
    return CurrentUser(user_id=x_user_id, college_id=x_college_id, role=x_role)


def require_permission(permission: Permission):
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission.value}",
            )
        return current_user

    return dependency
