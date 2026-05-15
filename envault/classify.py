"""classify.py — Categorize env keys into logical groups (e.g. database, auth, service)."""

import re
from typing import Dict, List, Optional

# Built-in category patterns: category -> list of regex patterns
_DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "database": [r"DB_", r"DATABASE_", r"POSTGRES", r"MYSQL", r"MONGO", r"REDIS", r"SQLITE"],
    "auth": [r"AUTH_", r"JWT_", r"OAUTH", r"SECRET", r"PASSWORD", r"PASSWD", r"TOKEN"],
    "api": [r"API_", r"API$", r"ENDPOINT", r"BASE_URL", r"SERVICE_URL"],
    "cloud": [r"AWS_", r"GCP_", r"AZURE_", r"S3_", r"GCS_"],
    "logging": [r"LOG_", r"LOGGING_", r"SENTRY_", r"DATADOG_"],
    "feature": [r"FEATURE_", r"FLAG_", r"ENABLE_", r"DISABLE_"],
    "app": [r"APP_", r"APPLICATION_", r"ENV$", r"ENVIRONMENT", r"DEBUG", r"PORT", r"HOST"],
}


def classify_key(key: str, categories: Optional[Dict[str, List[str]]] = None) -> Optional[str]:
    """Return the first matching category for a key, or None if uncategorized."""
    cats = categories if categories is not None else _DEFAULT_CATEGORIES
    upper = key.upper()
    for category, patterns in cats.items():
        for pattern in patterns:
            if re.search(pattern, upper):
                return category
    return None


def classify_env(
    env: Dict[str, str],
    categories: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, List[str]]:
    """Classify all keys in an env dict.

    Returns a dict mapping category -> list of keys.
    Keys that match no category are placed under 'uncategorized'.
    """
    result: Dict[str, List[str]] = {}
    for key in env:
        cat = classify_key(key, categories) or "uncategorized"
        result.setdefault(cat, []).append(key)
    # Sort keys within each category for determinism
    for cat in result:
        result[cat].sort()
    return result


def keys_in_category(
    env: Dict[str, str],
    category: str,
    categories: Optional[Dict[str, List[str]]] = None,
) -> List[str]:
    """Return all keys from env that belong to the given category."""
    classified = classify_env(env, categories)
    return classified.get(category, [])


def list_categories(categories: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Return sorted list of known category names."""
    cats = categories if categories is not None else _DEFAULT_CATEGORIES
    return sorted(cats.keys())
