from dataclasses import dataclass
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from database.models import User
from database.repositories import UserRepository
from database.schemas import UserCreate, UserAuth

from settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@dataclass(kw_only=True, frozen=True, slots=True)
class AuthService:
    user_repository: UserRepository
    settings: any

    def register_user(self, user_data: UserCreate) -> User | None:
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            return None
        hashed_password = pwd_context.hash(user_data.password)
        user = User(
            email=user_data.email,
            nickname=user_data.nickname,
            hashed_password=hashed_password
        )
        return self.user_repository.create(user)

    def authenticate_user(self, user_data: UserAuth):
        user = self.user_repository.get_by_email(user_data.email)
        if not user:
            return None
        if not pwd_context.verify(user_data.password, user.hashed_password):
            return None
        return user

    def create_access_token(self, subject: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {"sub": subject, "exp": expire}
        token = jwt.encode(payload, self.settings.secret_key, algorithm=self.settings.algorithm)
        return token

    def user_by_id(self, user_id:id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return user