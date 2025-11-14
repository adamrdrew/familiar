"""Environment variable utilities."""

import os
from typing import Dict, Any


def get_env_vars(prefix: str = "") -> Dict[str, str]:
    """Get environment variables, optionally filtered by prefix.

    Args:
        prefix: Optional prefix to filter environment variables.
                If provided, only variables starting with this prefix are returned,
                and the prefix is removed from the keys.

    Returns:
        Dictionary of environment variable key-value pairs.

    Example:
        >>> os.environ["APP_URL"] = "http://localhost:3000"
        >>> os.environ["APP_USER"] = "testuser"
        >>> get_env_vars("APP_")
        {"URL": "http://localhost:3000", "USER": "testuser"}
    """
    if not prefix:
        return dict(os.environ)

    filtered = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix from key
            filtered_key = key[len(prefix) :]
            filtered[filtered_key] = value

    return filtered
