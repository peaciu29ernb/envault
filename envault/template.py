"""Template rendering: substitute .env values into template strings."""

import re
from typing import Dict, Optional

# Matches ${VAR_NAME} or $VAR_NAME patterns
_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


class MissingVariableError(KeyError):
    """Raised when a template references a variable not present in the env dict."""


def render_template(template: str, env: Dict[str, str], strict: bool = True) -> str:
    """Substitute env variables into *template*.

    Args:
        template: A string containing ``${VAR}`` or ``$VAR`` placeholders.
        env:      Mapping of variable names to their values.
        strict:   If *True* (default), raise :class:`MissingVariableError` for
                  any placeholder whose key is absent from *env*.
                  If *False*, leave unresolved placeholders unchanged.

    Returns:
        The rendered string with placeholders replaced.
    """

    def _replace(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in env:
            return env[key]
        if strict:
            raise MissingVariableError(f"Template variable '${key}' not found in env")
        return match.group(0)  # leave as-is

    return _PATTERN.sub(_replace, template)


def render_file(
    template_path: str,
    env: Dict[str, str],
    output_path: Optional[str] = None,
    strict: bool = True,
) -> str:
    """Read a template file, render it, and optionally write the result.

    Args:
        template_path: Path to the template file.
        env:           Env variable mapping.
        output_path:   If given, write the rendered content to this path.
        strict:        Passed through to :func:`render_template`.

    Returns:
        The rendered content as a string.
    """
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()

    rendered = render_template(template, env, strict=strict)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(rendered)

    return rendered


def list_placeholders(template: str) -> list:
    """Return a sorted, deduplicated list of variable names used in *template*."""
    return sorted(
        {m.group(1) or m.group(2) for m in _PATTERN.finditer(template)}
    )
