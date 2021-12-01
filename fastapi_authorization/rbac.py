from __future__ import annotations

from inspect import getfile, signature

from fastapi import Depends, params
from fastapi.exceptions import HTTPException

from fastapi_authorization.utils import normalize_list

try:
    import rich.repr
except ModuleNotFoundError:  # pragma: no cover
    ...


class RBAC:
    def __init__(self, role_callback: str, roles: list[Role | str] | None = None):
        self.role_callback = role_callback
        self.roles = normalize_list(roles, Role) if roles else []

    def add_role(
        self,
        name: str,
        *,
        description: str | None = None,
        permissions: list[Scope | str] | None = None,
    ) -> None:
        role = Role(name, description, permissions)
        self.roles.append(role)

    def add_permissions(self, role: str, permissions: list[Scope | str]) -> None:
        if role not in self.roles:
            raise RuntimeError(f"Role {role} does not exist")
        index = self.roles.index(role)
        self.roles[index].add_permissions(permissions)

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

    def __repr__(self) -> str:
        clb_file = getfile(self.role_callback)
        clb_path = f"{clb_file}:{self.role_callback.__qualname__}"
        return f"<RBAC(role_callback='{clb_path}', roles={self.roles})>"

    def __rich_repr__(self) -> "rich.repr.Result":
        clb_file = getfile(self.role_callback)
        clb_path = f"{clb_file}:{self.role_callback.__qualname__}"
        yield "role_callback", clb_path
        yield "roles", self.roles


class Role:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        scopes: list[Scope | str] | None = None,
    ):
        self.name = name
        self.description = description
        self.permissions = normalize_list(scopes, Scope) if scopes else []

    def add_permissions(self, scopes: list[Scope | str]) -> None:
        scopes = normalize_list(scopes, Scope)
        self.permissions.extend(scopes)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, str):
            return __o == self.name
        elif isinstance(__o, type(self)):
            return __o.name == self.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<Role('{self.name}', permissions={self.permissions})>"

    def __rich_repr__(self) -> "rich.repr.Result":
        yield self.name
        yield "permissions", self.permissions


class Scope:
    def __init__(self, name: str, description: str | None = None):
        self.name = name
        self.description = description

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, str):
            return __o == self.name
        elif isinstance(__o, type(self)):
            return __o.name == self.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        if self.description:
            return f"<Permission('{self.name}', description='{self.description}')>"
        return f"<Permission('{self.name}')>"

    def __rich_repr__(self) -> "rich.repr.Result":
        yield self.scope
        if self.description:
            yield "description", self.description
