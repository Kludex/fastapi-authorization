from __future__ import annotations

from inspect import signature
from typing import List

from fastapi import Depends, params
from fastapi.exceptions import HTTPException


class RBAC:
    def __init__(self, role_callback: str, roles: List[Role] | None = None):
        self.role_callback = role_callback
        self.roles = roles or []

    def add_role(self, name: str, description: str | None = None) -> None:
        self.roles.append(Role(name, description))

    def add_permission(
        self, role: str, scope: str, *, description: str | None = None
    ) -> None:
        if role not in self.roles:
            self.add_role(role)
        index = self.roles.index(role)
        self.roles[index].add_permission(scope, description)

    def Permission(self, scope: str) -> params.Depends:
        def allow(role: str) -> bool:
            if role not in self.roles:
                raise HTTPException(status_code=403, detail="Forbidden")
            scopes = self.roles[self.roles.index(role)].permissions
            if scope not in scopes:
                raise HTTPException(status_code=403, detail="Forbidden")

        sig = signature(allow)
        sig = sig.replace(
            parameters=[
                sig.parameters["role"].replace(default=Depends(self.role_callback))
            ]
        )
        allow.__signature__ = sig
        return params.Depends(dependency=allow, use_cache=True)


class Role:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        permissions: List[Permission] | None = None,
    ):
        self.name = name
        self.description = description
        self.permissions = permissions or []

    def add_permission(self, scope: str, description: str | None = None) -> None:
        self.permissions.append(Permission(scope, description))

    def __eq__(self, __o: object) -> bool:
        return __o == self.name


class Permission:
    def __init__(self, scope: str, description: str | None = None):
        self.scope = scope
        self.description = description

    def __eq__(self, __o: object) -> bool:
        return __o == self.scope
