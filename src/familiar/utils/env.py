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
            filtered_key = key[len(prefix):]
            filtered[filtered_key] = value
    
    return filtered


def get_required_env(key: str) -> str:
    """Get required environment variable or raise error.
    
    Args:
        key: Environment variable name.
    
    Returns:
        Environment variable value.
    
    Raises:
        ValueError: If environment variable is not set.
    """
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def get_optional_env(key: str, default: str = "") -> str:
    """Get optional environment variable with default.
    
    Args:
        key: Environment variable name.
        default: Default value if variable is not set.
    
    Returns:
        Environment variable value or default.
    """
    return os.environ.get(key, default)


def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable.
    
    Recognizes: true, 1, yes, on (case-insensitive) as True.
    
    Args:
        key: Environment variable name.
        default: Default value if variable is not set.
    
    Returns:
        Boolean value.
    """
    value = os.environ.get(key, "").lower()
    if not value:
        return default
    return value in ("true", "1", "yes", "on")

