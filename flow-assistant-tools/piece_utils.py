"""Utility helpers for working with piece data returned by the Activepieces API."""

from typing import Any, Dict, List


def normalize_collection(collection: Any) -> Dict[str, Any]:
    """Return a dictionary representation for iterable collections when possible."""

    if isinstance(collection, dict):
        return collection

    if isinstance(collection, list):
        return {str(index): value for index, value in enumerate(collection)}

    return {}


def count_collection(collection: Any) -> int:
    """Return a count for the provided collection regardless of representation."""

    if isinstance(collection, (list, dict, tuple, set)):
        return len(collection)

    if isinstance(collection, int):
        return collection

    return 0


def get_categories(value: Any) -> List[str]:
    """Return a safe list of categories."""

    if isinstance(value, list):
        return value

    return []

