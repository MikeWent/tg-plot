from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from helpers.settings import settings

security = HTTPBasic()


def auth_required(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if settings.admin_password and str(credentials.password) != (
        settings.admin_password
    ):
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Basic"},
        )
