from hashlib import sha256
from typing import Annotated, Coroutine

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from helpers.settings import settings

security = HTTPBasic()


def password_hash(password: str) -> str:
    return sha256(password.encode() + settings.app_secret_key.encode()).hexdigest()


def set_password(password: str) -> None:
    settings.admin_password_hash = password_hash(password)
    settings.save()


def auth_required(view: bool = False):
    async def _auth_required(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
    ):
        if view and (not settings.view_password_required):
            return
        if (
            settings.admin_password_hash
            and password_hash(credentials.password) != settings.admin_password_hash
        ):
            raise HTTPException(
                status_code=401,
                headers={"WWW-Authenticate": "Basic"},
            )

    return _auth_required
