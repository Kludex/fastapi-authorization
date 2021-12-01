from __future__ import annotations

from inspect import Parameter, Signature
from typing import Any, Callable, Sequence

from fastapi import Depends, params


class Policy:
    def __init__(
        self, resource: str, action: str, conditions: Sequence[Callable[..., None]]
    ):
        self.resource = resource
        self.action = action
        self.conditions = conditions

    def __eq__(self, other: object) -> bool:
        if hasattr(other, "__len__") and len(other) == 2:
            return other[0] == self.resource and other[1] == self.action
        return False


class ABAC:
    def __init__(self, policies: list[Policy] | None = None) -> None:
        self.policies = policies or []

    def add_policy(
        self, resource: str, action: str, conditions: Sequence[Callable[..., None]]
    ) -> None:
        self.policies.append(Policy(resource, action, conditions))

    def Permission(self, resource: str, action: str) -> params.Depends:
        current_policy = None
        for policy in self.policies:
            if (resource, action) == policy:
                current_policy = policy

        if current_policy is None:
            raise RuntimeError(f"No policy for {resource}:{action} provided.")

        def allow(**conditions) -> Any:
            return conditions

        parameters = []
        for condition in current_policy.conditions:
            parameters.append(
                Parameter(
                    name=condition.__name__,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(condition),
                )
            )
        allow.__signature__ = Signature(parameters)
        return params.Depends(dependency=allow, use_cache=True)
