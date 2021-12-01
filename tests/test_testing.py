from fastapi import FastAPI

from fastapi_authorization.rbac import RBAC
from fastapi_authorization.testing import auto_test_protected_endpoints

auth = RBAC(lambda: "admin")
auth.add_role("admin", permissions=["user:create", "user:read"])
auth.add_role("superadmin", permissions=["admin:create", "admin:read"])
auth.add_role("user", permissions=["user:read"])

app = FastAPI()


@app.get("/", dependencies=[auth.Permission("user:read")])
def get_endpoint():
    ...


auto_test_protected_endpoints(app, auth)
