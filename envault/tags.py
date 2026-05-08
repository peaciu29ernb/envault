"""
envault/tags.py — Tag management for env variables.

Allows users to annotate env keys with tags (e.g. 'secret', 'optional',
'infra') and query/filter by tag.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# Tag registry structure:
# { "project": { "KEY": ["tag1", "tag2"], ... } }
_TagRegistry = Dict[str, Dict[str, List[str]]]


def add_tag(registry: _TagRegistry, project: str, key: str, tag: str) -> _TagRegistry:
    """Add a tag to an env key for a given project."""
    project_tags = registry.setdefault(project, {})
    key_tags = project_tags.setdefault(key, [])
    if tag not in key_tags:
        key_tags.append(tag)
    return registry


def remove_tag(registry: _TagRegistry, project: str, key: str, tag: str) -> bool:
    """Remove a tag from an env key. Returns True if removed, False if not found."""
    try:
        key_tags = registry[project][key]
    except KeyError:
        return False
    if tag in key_tags:
        key_tags.remove(tag)
        return True
    return False


def get_tags(registry: _TagRegistry, project: str, key: str) -> List[str]:
    """Return all tags for a given project key."""
    return list(registry.get(project, {}).get(key, []))


def keys_with_tag(registry: _TagRegistry, project: str, tag: str) -> List[str]:
    """Return all keys in a project that have a specific tag."""
    return [
        key
        for key, tags in registry.get(project, {}).items()
        if tag in tags
    ]


def all_tags(registry: _TagRegistry, project: str) -> Dict[str, List[str]]:
    """Return the full tag map for a project."""
    return dict(registry.get(project, {}))


def clear_tags(registry: _TagRegistry, project: str, key: str) -> _TagRegistry:
    """Remove all tags from a key."""
    if project in registry and key in registry[project]:
        del registry[project][key]
    return registry
