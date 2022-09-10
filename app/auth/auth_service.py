import time
from dataclasses import dataclass

import jwt  # type: ignore
from bcrypt import checkpw, gensalt, hashpw

from ..internal.exceptions import ServiceException
from ..internal.models import User, UserCreate
from ..internal.repository import RepositoryProtocol
from ..settings import Settings
from .models import LoginResponse

settings = Settings()


def sign_jwt(user: User) -> str:
    payload = {
        "user_id": user.uuid.hex,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "expires": time.time() + 86400,
    }
    token = jwt.encode(payload, settings.AUTH_SECRET, algorithm=settings.AUTH_ALGORITHM)

    return token


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.AUTH_SECRET, algorithms=[settings.AUTH_ALGORITHM]
        )
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:
        return {}


def get_hashed_password(plain_text_password: str) -> bytes:
    return hashpw(plain_text_password.encode("utf8"), gensalt())


def check_password(plain_text_password: str, hashed_password: str) -> bool:
    return checkpw(plain_text_password.encode("utf8"), hashed_password.encode("utf8"))


@dataclass()
class NotAuthorizedException(ServiceException):
    code: int = 401
    message: str = "User is not authorized"


@dataclass()
class BadAuthRequestException(ServiceException):
    code: int = 401
    message: str = "Incorrect username or password"


class AuthService:
    def __init__(self, repository: RepositoryProtocol[User]):
        self.repo = repository

    async def login(self, username: str, password: str) -> LoginResponse:
        user: User | None = await self.repo.findOne(User.username == username)

        if not user:
            raise NotAuthorizedException()

        if not check_password(password, user.hashed_password):
            raise NotAuthorizedException()

        jwt = sign_jwt(user)

        return LoginResponse(access_token=jwt)

    async def signup(self, user: UserCreate) -> bool:
        existing_user: User | None = await self.repo.findOne(
            User.username == user.username
        )

        if existing_user:
            raise BadAuthRequestException(
                message="A user with that username already exists."
            )

        hashed_password = get_hashed_password(user.password)
        db_user: User = User.from_orm(user, update={"hashed_password": hashed_password})

        await self.repo.add(db_user)

        return True
