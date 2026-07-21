from app.models.department import Department

MOCK_DEPARTMENTS = {
    "ed": Department(id="dept-1", name="Emergency Department", description="ER triage and acute care"),
    "micu": Department(id="dept-2", name="Medical ICU", description="General medical intensive care unit"),
    "sicu": Department(id="dept-3", name="Surgical ICU", description="Post-operative surgical intensive care"),
    "ccu": Department(id="dept-4", name="Cardiac ICU", description="Coronary and cardiovascular intensive care"),
    "picu": Department(id="dept-5", name="Pediatric ICU", description="Pediatric intensive care unit"),
    "lab": Department(id="dept-6", name="Clinical Laboratory", description="Diagnostic pathology and lab tests"),
    "admin": Department(id="dept-7", name="Administration", description="Hospital management and administrative IT"),
}

class DepartmentRepository:
    @staticmethod
    def get_all_departments() -> list[Department]:
        return list(MOCK_DEPARTMENTS.values())

    @staticmethod
    def get_by_name(name: str) -> Department | None:
        for d in MOCK_DEPARTMENTS.values():
            if d.name.lower() == name.lower():
                return d
        return None
