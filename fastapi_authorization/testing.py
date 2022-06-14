from __future__ import annotations

import inspect
from typing import Sequence, Union

from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastapi_authorization.abac import ABAC
from fastapi_authorization.rbac import RBAC


def auto_test_protected_endpoints(
    app: FastAPI, auth: Union[RBAC, ABAC], exclude: Sequence[str] = ()
) -> None:
    module_name = f"fastapi_authorization.{auth.__class__.__name__.lower()}"

    def test_auto_protect_endpoints():
        unprotected = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                protected = False
                for dependency in route.dependencies:
                    if module_name == dependency.dependency.__module__:
                        protected = True
                if protected or route.name in exclude:
                    continue
                unprotected.append(route.name)  # pragma: no cover
        assert unprotected == [], f"Unprotected routes: {unprotected}"

    called_from = inspect.stack()[1]
    module = inspect.getmodule(called_from[0])

    setattr(module, test_auto_protect_endpoints.__name__, test_auto_protect_endpoints)
