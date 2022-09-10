import uvicorn  # type: ignore
from fastapi import Body, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth_service import AuthService
from app.auth.models import LoginResponse
from app.dependencies import auth_service, get_current_user
from app.internal.exceptions import ServiceException
from app.internal.models import UserCreate

app = FastAPI()


# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers
@app.exception_handler(ServiceException)
async def service_exception_handler(
    request: Request, exc: ServiceException
) -> JSONResponse:
    headers: dict | None = None
    if exc.code == 401:
        headers = {"WWW-Authenticate": "Bearer"}

    return JSONResponse(
        status_code=exc.code, content={"message": exc.message}, headers=headers
    )


@app.get("/ping")
def pong() -> dict:
    return {"ping": "pong!"}


@app.get("/me")
def me(user: dict = Depends(get_current_user)) -> dict:
    return user


@app.post("/signup", tags=["user"], status_code=status.HTTP_200_OK)
async def create_user(
    user: UserCreate = Body(...), auth_service: AuthService = Depends(auth_service)
) -> bool:
    return await auth_service.signup(user)


@app.post("/login", tags=["auth"], response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(auth_service),
) -> LoginResponse:
    return await auth_service.login(form_data.username, form_data.password)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
