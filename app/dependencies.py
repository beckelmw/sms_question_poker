from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .auth.auth_service import AuthService, NotAuthorizedException, decode_jwt
from .internal.models import User
from .internal.repository import Repository, RepositoryProtocol

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    user = decode_jwt(token)
    if not user:
        raise NotAuthorizedException()
    return user


def auth_service(
    repo: RepositoryProtocol[User] = Depends(Repository(model=User)),
) -> AuthService:
    return AuthService(repo)
