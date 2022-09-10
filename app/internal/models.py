import uuid as uuid_pkg
from datetime import datetime

from pydantic import EmailStr, validator
from sqlalchemy import text
from sqlmodel import Field, SQLModel


# https://medium.com/@estretyakov/the-ultimate-async-setup-fastapi-sqlmodel-alembic-pytest-ae5cdcfed3d4
class UUIDModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
    )


# https://medium.com/@estretyakov/the-ultimate-async-setup-fastapi-sqlmodel-alembic-pytest-ae5cdcfed3d4
class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class UserBase(SQLModel):
    @validator("username")
    def must_be_beckelman_net(cls, v: str) -> str:
        if not v.endswith("@beckelman.net"):
            raise ValueError("Username must end with @beckelman.net")
        return v

    first_name: str
    last_name: str
    username: EmailStr = Field(index=True, sa_column_kwargs={"unique": True})


class User(UserBase, UUIDModel, table=True):
    __tablename__ = "users"
    hashed_password: str


class UserCreate(UserBase):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "jdoe@beckelman.net",
                "password": "pass@word",
            }
        }


class UserLoginResponse(SQLModel):
    uuid: uuid_pkg.UUID
    access_token: str

    class Config:
        schema_extra = {"example": {"id": "1", "access_token": "<your access token>"}}
