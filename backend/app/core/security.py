from enum import StrEnum

from fastapi import Depends, Header, HTTPException, status


class Permission(StrEnum):
    STUDENT_READ = "student:read"
    STUDENT_WRITE = "student:write"
    STUDENT_DELETE = "student:delete"
    STUDENT_PROMOTE = "student:promote"
    STUDENT_ALUMNI = "student:alumni"
    DOCUMENT_VERIFY = "document:verify"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "platform_super_admin": set(Permission),
    "college_owner": set(Permission),
    "principal": set(Permission),
    "administrator": set(Permission),
    "admission_officer": {
        Permission.STUDENT_READ,
        Permission.STUDENT_WRITE,
        Permission.DOCUMENT_VERIFY,
    },
    "teacher": {Permission.STUDENT_READ},
    "parent": {Permission.STUDENT_READ},
    "student": {Permission.STUDENT_READ},
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
