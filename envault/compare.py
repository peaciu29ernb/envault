"""Compare two vault files or env dicts and produce a structured report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault


@dataclass
class CompareReport:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.changed)

    def to_dict(self) -> dict:
        return {
            "only_in_a": self.only_in_a,
            "only_in_b": self.only_in_b,
            "changed": {k: {"a": v[0], "b": v[1]} for k, v in self.changed.items()},
            "unchanged": self.unchanged,
        }


def compare_dicts(a: Dict[str, str], b: Dict[str, str]) -> CompareReport:
    """Compare two env dicts and return a CompareReport."""
    keys_a = set(a)
    keys_b = set(b)

    report = CompareReport()
    report.only_in_a = sorted(keys_a - keys_b)
    report.only_in_b = sorted(keys_b - keys_a)

    for key in sorted(keys_a & keys_b):
        if a[key] != b[key]:
            report.changed[key] = (a[key], b[key])
        else:
            report.unchanged.append(key)

    return report


def compare_vaults(
    vault_a: str,
    vault_b: str,
    key_a: Optional[bytes] = None,
    key_b: Optional[bytes] = None,
    password_a: Optional[str] = None,
    password_b: Optional[str] = None,
) -> CompareReport:
    """Load two vault files and compare their decrypted contents."""
    env_a = load_vault(vault_a, key=key_a, password=password_a)
    env_b = load_vault(vault_b, key=key_b, password=password_b)
    return compare_dicts(env_a, env_b)


def format_compare_report(report: CompareReport, *, show_unchanged: bool = False) -> str:
    """Render a human-readable comparison report."""
    lines: List[str] = []

    for key in report.only_in_a:
        lines.append(f"< {key}  (only in A)")
    for key in report.only_in_b:
        lines.append(f"> {key}  (only in B)")
    for key, (val_a, val_b) in sorted(report.changed.items()):
        lines.append(f"~ {key}")
        lines.append(f"    A: {val_a}")
        lines.append(f"    B: {val_b}")
    if show_unchanged:
        for key in report.unchanged:
            lines.append(f"  {key}  (unchanged)")

    if not lines:
        return "No differences found."
    return "\n".join(lines)
