"""Format conversion utilities for env dictionaries.

Supports converting between .env, JSON, TOML-style, and INI-style
representations of environment variable maps.
"""

import json
import configparser
import io
from typing import Dict, Optional


class FormatError(ValueError):
    """Raised when parsing or formatting fails."""
    pass


def from_env_string(text: str) -> Dict[str, str]:
    """Parse a .env-style string into a dict, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise FormatError(f"Line {lineno}: missing '=' in {raw!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if not key:
            raise FormatError(f"Line {lineno}: empty key in {raw!r}")
        result[key] = value
    return result


def to_env_string(env: Dict[str, str]) -> str:
    """Serialize a dict to a .env-style string."""
    lines = []
    for key, value in sorted(env.items()):
        if " " in value or "#" in value or not value:
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def from_json_string(text: str) -> Dict[str, str]:
    """Parse a JSON object string into a flat string dict."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FormatError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FormatError("JSON root must be an object")
    return {str(k): str(v) for k, v in data.items()}


def to_json_string(env: Dict[str, str], indent: int = 2) -> str:
    """Serialize a dict to a pretty-printed JSON string."""
    return json.dumps(env, indent=indent, sort_keys=True)


def from_ini_string(text: str, section: str = "env") -> Dict[str, str]:
    """Parse an INI-style string (single section) into a dict."""
    parser = configparser.RawConfigParser()
    parser.optionxform = str  # preserve key case
    try:
        parser.read_string(text)
    except configparser.Error as exc:
        raise FormatError(f"Invalid INI: {exc}") from exc
    if not parser.has_section(section):
        raise FormatError(f"INI section [{section}] not found")
    return dict(parser.items(section))


def to_ini_string(env: Dict[str, str], section: str = "env") -> str:
    """Serialize a dict to an INI-style string under a named section."""
    parser = configparser.RawConfigParser()
    parser.optionxform = str
    parser.add_section(section)
    for key, value in sorted(env.items()):
        parser.set(section, key, value)
    buf = io.StringIO()
    parser.write(buf)
    return buf.getvalue()
