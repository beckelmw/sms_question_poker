from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_TEST: str = ""
    AUTH_SECRET: str
    AUTH_ALGORITHM: str

    class Config:
        env_file = ".env"
