"""Variable interpolation utilities for test steps."""

import re
from typing import Dict


def interpolate_variables(text: str, variables: Dict[str, str]) -> str:
    """Interpolate ${VAR} style variables in text.

    Replaces all occurrences of ${VAR_NAME} with values from the variables dict.
    If a variable is not found, it is left unchanged.

    Args:
        text: Text containing ${VAR} style placeholders.
        variables: Dictionary of variable name -> value mappings.

    Returns:
        Text with variables interpolated.

    Example:
        >>> text = "Visit ${APP_URL} and login as ${USERNAME}"
        >>> vars = {"APP_URL": "http://localhost", "USERNAME": "admin"}
        >>> interpolate_variables(text, vars)
        "Visit http://localhost and login as admin"
    """
    if not text:
        return text

    # Pattern matches ${VAR_NAME} with alphanumeric and underscore
    pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"

    def replacer(match):
        var_name = match.group(1)
        # Return the value if found, otherwise leave the placeholder unchanged
        return variables.get(var_name, match.group(0))

    return re.sub(pattern, replacer, text)


def extract_variables(text: str) -> list[str]:
    """Extract variable names from text containing ${VAR} style placeholders.

    Args:
        text: Text containing ${VAR} style placeholders.

    Returns:
        List of unique variable names found in the text.

    Example:
        >>> text = "Visit ${APP_URL} and login as ${USERNAME} at ${APP_URL}"
        >>> extract_variables(text)
        ["APP_URL", "USERNAME"]
    """
    if not text:
        return []

    pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"
    matches = re.findall(pattern, text)

    # Return unique variable names in order of first appearance
    seen = set()
    unique = []
    for var in matches:
        if var not in seen:
            seen.add(var)
            unique.append(var)

    return unique
