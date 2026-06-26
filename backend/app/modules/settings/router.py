from fastapi import APIRouter

router = APIRouter()


@router.get("/tenant-template")
def tenant_template() -> dict[str, object]:
    """Return the configurable tenant settings planned for each college."""
    return {
        "branding": ["name", "logo", "address", "theme"],
        "academics": ["sessions", "subjects", "grading_policy", "academic_calendar"],
        "finance": ["fee_heads", "fee_structures", "challan_templates"],
        "modules": ["admissions", "attendance", "examination", "fees", "reports"],
    }
