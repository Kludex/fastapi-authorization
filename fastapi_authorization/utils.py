from __future__ import annotations

from typing import Type, TypeVar

T = TypeVar("T")


def normalize_list(items: list[str | T], type_: Type[T]) -> list[T]:
    """Normalize a list of items to a list of the specified type.

    This solution assumes that T is instantiable with a single string argument.

    Args:
        items (list[str | T]): The list of items to normalize.
        type_ (Type[T]): The type of the items in the output list.

    Returns:
        list[T]: The normalized list.
    """
    normalized_items = []
    for item in items:
        if isinstance(item, type_):
            normalized_items.append(item)
        else:
            normalized_items.append(type_(item))
    return normalized_items
