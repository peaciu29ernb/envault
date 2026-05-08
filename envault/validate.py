"""Validation utilities for envault: check env dicts against a schema/spec file."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ValidationError:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __repr__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"

    def to_dict(self) -> dict:
        return {"key": self.key, "message": self.message, "severity": self.severity}


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def all_issues(self) -> List[ValidationError]:
        return self.errors + self.warnings


def load_schema(schema_path: str | Path) -> Dict[str, dict]:
    """Load a JSON schema file mapping key names to spec dicts.

    Each entry may have:
      - required (bool, default True)
      - pattern (str regex, optional)
      - allowed_values (list, optional)
    """
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with open(path, "r") as fh:
        return json.load(fh)


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, dict],
) -> ValidationResult:
    """Validate an env dict against a schema. Returns a ValidationResult."""
    import re

    result = ValidationResult()

    for key, spec in schema.items():
        required = spec.get("required", True)
        if key not in env:
            if required:
                result.errors.append(
                    ValidationError(key, "required key is missing", "error")
                )
            else:
                result.warnings.append(
                    ValidationError(key, "optional key is not set", "warning")
                )
            continue

        value = env[key]

        if pattern := spec.get("pattern"):
            if not re.fullmatch(pattern, value):
                result.errors.append(
                    ValidationError(
                        key,
                        f"value does not match pattern '{pattern}'",
                        "error",
                    )
                )

        if allowed := spec.get("allowed_values"):
            if value not in allowed:
                result.errors.append(
                    ValidationError(
                        key,
                        f"value '{value}' not in allowed values {allowed}",
                        "error",
                    )
                )

    return result
