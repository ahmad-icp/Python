from pydantic import BaseModel
from app.modules.student_portal.schemas import StudentPortalDashboard

class ParentPortalDashboard(BaseModel):
    children: list[StudentPortalDashboard]
    teacher_communication: list[dict[str, str]]
