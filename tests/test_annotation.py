"""Tests for envault.annotation."""

from __future__ import annotations

import pytest

from envault.annotation import (
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
    annotate_env,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_annotation(base_dir):
    set_annotation("DB_HOST", "Primary database host", base_dir=base_dir)
    assert get_annotation("DB_HOST", base_dir=base_dir) == "Primary database host"


def test_get_missing_annotation_returns_none(base_dir):
    assert get_annotation("MISSING_KEY", base_dir=base_dir) is None


def test_set_annotation_overwrites_existing(base_dir):
    set_annotation("API_KEY", "old note", base_dir=base_dir)
    set_annotation("API_KEY", "new note", base_dir=base_dir)
    assert get_annotation("API_KEY", base_dir=base_dir) == "new note"


def test_remove_annotation_returns_true(base_dir):
    set_annotation("SECRET", "some secret", base_dir=base_dir)
    assert remove_annotation("SECRET", base_dir=base_dir) is True
    assert get_annotation("SECRET", base_dir=base_dir) is None


def test_remove_missing_annotation_returns_false(base_dir):
    assert remove_annotation("GHOST", base_dir=base_dir) is False


def test_list_annotations_empty_when_none(base_dir):
    assert list_annotations(base_dir=base_dir) == {}


def test_list_annotations_returns_all(base_dir):
    set_annotation("A", "note-a", base_dir=base_dir)
    set_annotation("B", "note-b", base_dir=base_dir)
    result = list_annotations(base_dir=base_dir)
    assert result == {"A": "note-a", "B": "note-b"}


def test_annotations_are_project_isolated(base_dir):
    set_annotation("KEY", "proj1 note", project="proj1", base_dir=base_dir)
    set_annotation("KEY", "proj2 note", project="proj2", base_dir=base_dir)
    assert get_annotation("KEY", project="proj1", base_dir=base_dir) == "proj1 note"
    assert get_annotation("KEY", project="proj2", base_dir=base_dir) == "proj2 note"


def test_annotate_env_maps_all_keys(base_dir):
    env = {"DB_HOST": "localhost", "PORT": "5432", "SECRET": "x"}
    set_annotation("DB_HOST", "host note", base_dir=base_dir)
    result = annotate_env(env, base_dir=base_dir)
    assert result["DB_HOST"] == "host note"
    assert result["PORT"] is None
    assert result["SECRET"] is None


def test_annotate_env_empty_env(base_dir):
    assert annotate_env({}, base_dir=base_dir) == {}
