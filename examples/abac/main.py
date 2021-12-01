from fastapi import Depends, FastAPI
from fastapi_authorization import ABAC


def get_user():
    return "user"


def user_is_admin(user=Depends(get_user)) -> None:
    ...


def get_property(property_id: int) -> dict:
    return "property"


def owns_property(property=Depends(get_property), user=Depends(get_user)) -> None:
    ...


auth = ABAC()
auth.add_policy("users", "read", conditions=[user_is_admin])
auth.add_policy("properties", "write", conditions=[owns_property])

app = FastAPI()


@app.get("/users", dependencies=[auth.Permission("users", "read")])
def get_users():
    ...


@app.post("/properties", dependencies=[auth.Permission("properties", "write")])
def create_property():
    ...
