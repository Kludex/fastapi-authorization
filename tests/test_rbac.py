import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_authorization.rbac import RBAC


def get_role_factory(role: str):
    return lambda: role


@pytest.mark.parametrize(
    "role, scope, status",
    [
        ("admin", "user:create", 200),
        ("admin", "admin:read", 403),
        ("superadmin", "admin:create", 200),
        ("user", "admin:create", 403),
        ("user", "user:read", 200),
    ],
)
def test_rbac(role: str, scope: str, status: int):
    auth = RBAC(get_role_factory(role))
    auth.add_role("admin", permissions=["user:create", "user:read"])
    auth.add_role("superadmin", permissions=["admin:create", "admin:read"])
    auth.add_role("user", permissions=["user:read"])

    app = FastAPI()

    @app.get("/", dependencies=[auth.Permission(scope)])
    def get_endpoint():
        ...

    client = TestClient(app)
    assert client.get("/").status_code == status, role
