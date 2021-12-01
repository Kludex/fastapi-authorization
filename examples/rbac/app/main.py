from fastapi import Depends, FastAPI
from pydantic import BaseModel

from fastapi_authorization.rbac import RBAC


class Token(BaseModel):
    role: str


def get_token():
    return Token(role="admin")


def role_callback(token: Token = Depends(get_token)) -> str:
    return token.role


auth = RBAC(role_callback, roles=["admin"])
auth.add_role("admin", permissions=["read:user"])

app = FastAPI()


@app.get("/", dependencies=[auth.Permission("read:user")])
def get_user():
    return {"Hello": "World"}


@app.get("/users")
def get_users():
    return {"Hello": "World"}
