import hashlib
import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.config import settings

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            if hashed_password.startswith("$2"):
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            pass
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> User | None:
        user = UserRepository.get_by_username(username)
        if not user:
            user = UserRepository.get_by_email(username)
            
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        # Add access token type tag
        to_encode.update({"type": "access"})
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        # Add refresh token type tag
        to_encode.update({"type": "refresh"})
        expire = datetime.now(timezone.utc) + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token signature has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
