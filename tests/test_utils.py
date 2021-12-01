import pytest

from fastapi_authorization.rbac import Role, Scope
from fastapi_authorization.utils import normalize_list


@pytest.mark.parametrize(
    "input,expected", [([Role("role"), "another"], [Role("role"), Role("another")])]
)
def test_normalize_list(input, expected):
    assert normalize_list(input, Role) == expected
