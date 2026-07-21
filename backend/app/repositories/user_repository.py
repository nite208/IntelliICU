import bcrypt
import uuid
from app.models.user import User
from app.database.session import SessionLocal
from app.database.models import DBUser

def hash_pw(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Seed users with department fields added (for mock fallback)
MOCK_USERS = {
    "admin": {
        "id": "usr-1",
        "username": "admin",
        "email": "admin@intelliicu.org",
        "hashed_password": hash_pw("admin123"),
        "role": "HospitalAdmin",
        "department": "Administration",
        "is_active": True
    },
    "reyes": {
        "id": "usr-2",
        "username": "reyes",
        "email": "reyes@intelliicu.org",
        "hashed_password": hash_pw("intensivist123"),
        "role": "ICUManager",
        "department": "Medical ICU",
        "is_active": True
    },
    "miller": {
        "id": "usr-3",
        "username": "miller",
        "email": "miller@intelliicu.org",
        "hashed_password": hash_pw("miller123"),
        "role": "Doctor",
        "department": "Medical ICU",
        "is_active": True
    }
}

class UserRepository:
    @staticmethod
    def get_by_username(username: str) -> User | None:
        try:
            db = SessionLocal()
            try:
                db_user = db.query(DBUser).filter(DBUser.username.ilike(username)).first()
                if db_user:
                    return User(
                        id=db_user.id,
                        username=db_user.username,
                        email=db_user.email,
                        hashed_password=db_user.hashed_password,
                        role=db_user.role,
                        department=db_user.department,
                        is_active=db_user.is_active,
                    )
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        user_dict = MOCK_USERS.get(username.lower())
        if not user_dict:
            return None
        return User(**user_dict)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        try:
            db = SessionLocal()
            try:
                db_user = db.query(DBUser).filter(DBUser.email.ilike(email)).first()
                if db_user:
                    return User(
                        id=db_user.id,
                        username=db_user.username,
                        email=db_user.email,
                        hashed_password=db_user.hashed_password,
                        role=db_user.role,
                        department=db_user.department,
                        is_active=db_user.is_active,
                    )
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        user_dict = next(
            (u for u in MOCK_USERS.values() if u["email"].lower() == email.lower()),
            None
        )
        if not user_dict:
            return None
        return User(**user_dict)

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        try:
            db = SessionLocal()
            try:
                db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
                if db_user:
                    return User(
                        id=db_user.id,
                        username=db_user.username,
                        email=db_user.email,
                        hashed_password=db_user.hashed_password,
                        role=db_user.role,
                        department=db_user.department,
                        is_active=db_user.is_active,
                    )
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        user_dict = next(
            (u for u in MOCK_USERS.values() if u["id"] == user_id),
            None
        )
        if not user_dict:
            return None
        return User(**user_dict)

    @staticmethod
    def list_users(search: str = None, role: str = None, department: str = None, page: int = 1, size: int = 10) -> tuple[list[User], int]:
        try:
            db = SessionLocal()
            try:
                query = db.query(DBUser)
                if search:
                    term = f"%{search}%"
                    query = query.filter(
                        (DBUser.username.ilike(term)) | (DBUser.email.ilike(term))
                    )
                if role and role.lower() != "all":
                    query = query.filter(DBUser.role.ilike(role))
                if department and department.lower() != "all":
                    query = query.filter(DBUser.department.ilike(department))
                    
                total = query.count()
                db_users = query.offset((page - 1) * size).limit(size).all()
                users = [
                    User(
                        id=u.id,
                        username=u.username,
                        email=u.email,
                        hashed_password=u.hashed_password,
                        role=u.role,
                        department=u.department,
                        is_active=u.is_active,
                    )
                    for u in db_users
                ]
                return users, total
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        filtered = list(MOCK_USERS.values())
        if search:
            term = search.lower()
            filtered = [
                u for u in filtered
                if term in u["username"].lower() or term in u["email"].lower()
            ]
        if role and role.lower() != "all":
            filtered = [u for u in filtered if u["role"].lower() == role.lower()]
        if department and department.lower() != "all":
            filtered = [
                u for u in filtered
                if u.get("department") and u["department"].lower() == department.lower()
            ]
            
        total = len(filtered)
        start = (page - 1) * size
        end = start + size
        users = [User(**u) for u in filtered[start:end]]
        return users, total

    @staticmethod
    def create_user(user_data: dict) -> User:
        try:
            db = SessionLocal()
            try:
                username = user_data["username"]
                email = user_data["email"]
                
                # Check constraints
                if db.query(DBUser).filter(DBUser.username.ilike(username)).first():
                    raise ValueError("Username already exists")
                if db.query(DBUser).filter(DBUser.email.ilike(email)).first():
                    raise ValueError("Email already exists")
                    
                uid = f"usr-{str(uuid.uuid4())[:8]}"
                db_user = DBUser(
                    id=uid,
                    username=username,
                    email=email,
                    hashed_password=user_data["hashed_password"],
                    role=user_data["role"],
                    department=user_data.get("department"),
                    is_active=True,
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                # Sync mock
                MOCK_USERS[username.lower()] = {
                    "id": uid,
                    "username": username,
                    "email": email,
                    "hashed_password": user_data["hashed_password"],
                    "role": user_data["role"],
                    "department": user_data.get("department"),
                    "is_active": True
                }
                
                return User(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    hashed_password=db_user.hashed_password,
                    role=db_user.role,
                    department=db_user.department,
                    is_active=db_user.is_active,
                )
            finally:
                db.close()
        except ValueError:
            raise
        except Exception:
            pass

        # Fallback to mock
        username = user_data["username"]
        email = user_data["email"]
        if username.lower() in MOCK_USERS:
            raise ValueError("Username already exists")
        if any(u["email"].lower() == email.lower() for u in MOCK_USERS.values()):
            raise ValueError("Email already exists")
            
        uid = f"usr-{str(uuid.uuid4())[:8]}"
        user_dict = {
            "id": uid,
            "username": username,
            "email": email,
            "hashed_password": user_data["hashed_password"],
            "role": user_data["role"],
            "department": user_data.get("department"),
            "is_active": True
        }
        MOCK_USERS[username.lower()] = user_dict
        return User(**user_dict)

    @staticmethod
    def update_user(user_id: str, update_data: dict) -> User | None:
        try:
            db = SessionLocal()
            try:
                db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
                if not db_user:
                    return None
                    
                email = update_data.get("email")
                if email and email.lower() != db_user.email.lower():
                    if db.query(DBUser).filter(DBUser.email.ilike(email), DBUser.id != user_id).first():
                        raise ValueError("Email already exists")
                        
                if "email" in update_data:
                    db_user.email = update_data["email"]
                if "role" in update_data:
                    db_user.role = update_data["role"]
                if "department" in update_data:
                    db_user.department = update_data["department"]
                if "is_active" in update_data:
                    db_user.is_active = update_data["is_active"]
                    
                db.commit()
                db.refresh(db_user)
                
                # Sync mock
                for u in MOCK_USERS.values():
                    if u["id"] == user_id:
                        u["email"] = db_user.email
                        u["role"] = db_user.role
                        u["department"] = db_user.department
                        u["is_active"] = db_user.is_active
                        break
                        
                return User(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    hashed_password=db_user.hashed_password,
                    role=db_user.role,
                    department=db_user.department,
                    is_active=db_user.is_active,
                )
            finally:
                db.close()
        except ValueError:
            raise
        except Exception:
            pass

        # Fallback to mock
        user_dict = next((u for u in MOCK_USERS.values() if u["id"] == user_id), None)
        if not user_dict:
            return None
            
        email = update_data.get("email")
        if email and email.lower() != user_dict["email"].lower():
            if any(u["email"].lower() == email.lower() and u["id"] != user_id for u in MOCK_USERS.values()):
                raise ValueError("Email already exists")
                
        user_dict["email"] = update_data.get("email", user_dict["email"])
        user_dict["role"] = update_data.get("role", user_dict["role"])
        user_dict["department"] = update_data.get("department", user_dict.get("department"))
        if "is_active" in update_data:
            user_dict["is_active"] = update_data["is_active"]
            
        return User(**user_dict)

    @staticmethod
    def set_password(user_id: str, hashed_password: str) -> bool:
        try:
            db = SessionLocal()
            try:
                db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
                if not db_user:
                    return False
                db_user.hashed_password = hashed_password
                db.commit()
                
                # Sync mock
                for u in MOCK_USERS.values():
                    if u["id"] == user_id:
                        u["hashed_password"] = hashed_password
                        break
                return True
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to mock
        user_dict = next((u for u in MOCK_USERS.values() if u["id"] == user_id), None)
        if not user_dict:
            return False
        user_dict["hashed_password"] = hashed_password
        return True
