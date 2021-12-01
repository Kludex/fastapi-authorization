from examples.rbac.app.main import app, auth
from fastapi_authorization.testing import auto_test_protected_endpoints

auto_test_protected_endpoints(app, auth, exclude=["get_users"])
