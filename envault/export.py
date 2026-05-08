"""Export decrypted .env contents to various formats."""

import json
from typing import Dict, Optional


def export_as_env(env_dict: Dict[str, str]) -> str:
    """Serialize env dict back to .env file format."""
    lines = []
    for key, value in env_dict.items():
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_as_json(env_dict: Dict[str, str], indent: int = 2) -> str:
    """Serialize env dict to JSON string."""
    return json.dumps(env_dict, indent=indent)


def export_as_shell(env_dict: Dict[str, str]) -> str:
    """Serialize env dict as shell export statements."""
    lines = []
    for key, value in env_dict.items():
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_as_docker(env_dict: Dict[str, str]) -> str:
    """Serialize env dict as Docker --env-file compatible format."""
    lines = []
    for key, value in env_dict.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


SUPPORTED_FORMATS = ("env", "json", "shell", "docker")


def export_env(env_dict: Dict[str, str], fmt: str = "env") -> str:
    """Export env dict in the specified format.

    Args:
        env_dict: Dictionary of environment variables.
        fmt: One of 'env', 'json', 'shell', 'docker'.

    Returns:
        Formatted string.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt == "env":
        return export_as_env(env_dict)
    elif fmt == "json":
        return export_as_json(env_dict)
    elif fmt == "shell":
        return export_as_shell(env_dict)
    elif fmt == "docker":
        return export_as_docker(env_dict)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
