"""Unit tests for envault.promote."""

from __future__ import annotations

import pytest

from envault.promote import PromoteError, promote_keys, promote_report


SOURCE = {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"}
TARGET = {"DB_HOST": "staging-db", "APP_ENV": "staging"}


def test_promote_all_keys_no_overwrite():
    result = promote_keys(SOURCE, TARGET, overwrite=False)
    assert result["DB_PORT"] == "5432"
    assert result["SECRET"] == "s3cr3t"
    # DB_HOST should NOT be overwritten
    assert result["DB_HOST"] == "staging-db"
    assert result["APP_ENV"] == "staging"


def test_promote_all_keys_with_overwrite():
    result = promote_keys(SOURCE, TARGET, overwrite=True)
    assert result["DB_HOST"] == "prod-db"
    assert result["DB_PORT"] == "5432"
    assert result["APP_ENV"] == "staging"


def test_promote_specific_keys():
    result = promote_keys(SOURCE, TARGET, keys=["DB_PORT"], overwrite=False)
    assert result["DB_PORT"] == "5432"
    assert "SECRET" not in result
    assert result["DB_HOST"] == "staging-db"


def test_promote_missing_key_raises():
    with pytest.raises(PromoteError, match="MISSING"):
        promote_keys(SOURCE, TARGET, keys=["MISSING"])


def test_promote_exclude_skips_keys():
    result = promote_keys(SOURCE, TARGET, exclude=["SECRET"], overwrite=True)
    assert "SECRET" not in result
    assert result["DB_HOST"] == "prod-db"


def test_promote_does_not_mutate_target():
    original_target = dict(TARGET)
    promote_keys(SOURCE, TARGET, overwrite=True)
    assert TARGET == original_target


def test_promote_empty_source_to_target():
    result = promote_keys({}, TARGET)
    assert result == TARGET


def test_promote_report_added():
    promoted = {"NEW_KEY": "value"}
    report = promote_report(SOURCE, {}, promoted)
    assert report[0]["action"] == "added"
    assert report[0]["key"] == "NEW_KEY"


def test_promote_report_overwritten():
    promoted = {"DB_HOST": "prod-db"}
    report = promote_report(SOURCE, {"DB_HOST": "old"}, promoted)
    assert report[0]["action"] == "overwritten"
    assert report[0]["old"] == "old"


def test_promote_report_unchanged():
    promoted = {"DB_HOST": "same"}
    report = promote_report(SOURCE, {"DB_HOST": "same"}, promoted)
    assert report[0]["action"] == "unchanged"


def test_promote_exclude_and_specific_keys_combined():
    result = promote_keys(
        SOURCE, TARGET,
        keys=["DB_HOST", "SECRET"],
        exclude=["SECRET"],
        overwrite=True,
    )
    assert result["DB_HOST"] == "prod-db"
    assert "SECRET" not in result or result.get("SECRET") == TARGET.get("SECRET")
