from app.models.role import Role, Permission
from app.database.session import SessionLocal
from app.database.models import DBRole, DBPermission

MOCK_PERMISSIONS = {
    "dashboard": Permission(id="perm-1", name="Dashboard", description="View dashboard stats and status"),
    "patients": Permission(id="perm-2", name="Patients", description="View patient list and profile telemetry"),
    "clinicalai": Permission(id="perm-3", name="ClinicalAI", description="Run sepsis AI risk analyses"),
    "alerts": Permission(id="perm-4", name="Alerts", description="Acknowledge, resolve, and manage alerts"),
    "timeline": Permission(id="perm-5", name="Timeline", description="Audit patient clinical events timeline log"),
    "reports": Permission(id="perm-6", name="Reports", description="Export patient timeline reports as PDF/CSV/JSON"),
    "analytics": Permission(id="perm-7", name="Analytics", description="View alerts response times and system analytics"),
    "usermanagement": Permission(id="perm-8", name="UserManagement", description="Manage administrative users"),
    "settings": Permission(id="perm-9", name="Settings", description="Modify clinical limits and configuration thresholds"),
}

MOCK_ROLES = {
    "superadmin": Role(
        id="role-1",
        name="SuperAdmin",
        permissions=[p.name for p in MOCK_PERMISSIONS.values()]
    ),
    "hospitaladmin": Role(
        id="role-2",
        name="HospitalAdmin",
        permissions=["Dashboard", "Patients", "Reports", "Analytics", "UserManagement", "Settings"]
    ),
    "icumanager": Role(
        id="role-3",
        name="ICUManager",
        permissions=["Dashboard", "Patients", "ClinicalAI", "Alerts", "Timeline", "Reports", "Analytics", "Settings"]
    ),
    "doctor": Role(
        id="role-4",
        name="Doctor",
        permissions=["Dashboard", "Patients", "ClinicalAI", "Alerts", "Timeline", "Reports", "Analytics"]
    ),
    "nurse": Role(
        id="role-5",
        name="Nurse",
        permissions=["Dashboard", "Patients", "Alerts", "Timeline", "Reports"]
    ),
    "labtechnician": Role(
        id="role-6",
        name="LabTechnician",
        permissions=["Dashboard", "Patients", "Reports"]
    ),
    "receptionist": Role(
        id="role-7",
        name="Receptionist",
        permissions=["Dashboard", "Patients"]
    ),
    "viewer": Role(
        id="role-8",
        name="Viewer",
        permissions=["Dashboard", "Patients"]
    )
}

class RBACRepository:
    @staticmethod
    def get_role_by_name(name: str) -> Role | None:
        try:
            db = SessionLocal()
            try:
                db_role = db.query(DBRole).filter(DBRole.name.ilike(name)).first()
                if db_role:
                    return Role(
                        id=db_role.id,
                        name=db_role.name,
                        permissions=[p.name for p in db_role.permissions]
                    )
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        return MOCK_ROLES.get(name.lower())

    @staticmethod
    def get_all_roles() -> list[Role]:
        try:
            db = SessionLocal()
            try:
                db_roles = db.query(DBRole).all()
                if db_roles:
                    return [
                        Role(
                            id=r.id,
                            name=r.name,
                            permissions=[p.name for p in r.permissions]
                        )
                        for r in db_roles
                    ]
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        return list(MOCK_ROLES.values())

    @staticmethod
    def get_all_permissions() -> list[Permission]:
        try:
            db = SessionLocal()
            try:
                db_perms = db.query(DBPermission).all()
                if db_perms:
                    return [
                        Permission(
                            id=p.id,
                            name=p.name,
                            description=p.description
                        )
                        for p in db_perms
                    ]
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        return list(MOCK_PERMISSIONS.values())

    @classmethod
    def get_permissions_for_role(cls, role_name: str) -> list[str]:
        role = cls.get_role_by_name(role_name)
        if not role:
            return []
        return role.permissions
