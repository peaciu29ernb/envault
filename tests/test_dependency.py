import pytest
from envault.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    all_dependencies,
    check_missing,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_dependency_creates_entry(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    deps = get_dependencies(base_dir, "myapp", "DB_URL")
    assert "DB_HOST" in deps


def test_add_dependency_no_duplicates(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    deps = get_dependencies(base_dir, "myapp", "DB_URL")
    assert deps.count("DB_HOST") == 1


def test_add_multiple_dependencies(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    add_dependency(base_dir, "myapp", "DB_URL", "DB_PORT")
    deps = get_dependencies(base_dir, "myapp", "DB_URL")
    assert set(deps) == {"DB_HOST", "DB_PORT"}


def test_get_dependencies_empty_when_none(base_dir):
    deps = get_dependencies(base_dir, "myapp", "UNKNOWN_KEY")
    assert deps == []


def test_remove_dependency_returns_true(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    result = remove_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    assert result is True
    assert get_dependencies(base_dir, "myapp", "DB_URL") == []


def test_remove_dependency_returns_false_when_absent(base_dir):
    result = remove_dependency(base_dir, "myapp", "DB_URL", "NONEXISTENT")
    assert result is False


def test_remove_last_dependency_cleans_up_key(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    remove_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    data = all_dependencies(base_dir, "myapp")
    assert "DB_URL" not in data


def test_get_dependents(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    add_dependency(base_dir, "myapp", "REDIS_URL", "DB_HOST")
    dependents = get_dependents(base_dir, "myapp", "DB_HOST")
    assert set(dependents) == {"DB_URL", "REDIS_URL"}


def test_get_dependents_empty_when_none(base_dir):
    dependents = get_dependents(base_dir, "myapp", "ORPHAN_KEY")
    assert dependents == []


def test_all_dependencies_returns_full_map(base_dir):
    add_dependency(base_dir, "myapp", "A", "B")
    add_dependency(base_dir, "myapp", "C", "D")
    data = all_dependencies(base_dir, "myapp")
    assert data == {"A": ["B"], "C": ["D"]}


def test_check_missing_returns_absent_deps(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    add_dependency(base_dir, "myapp", "DB_URL", "DB_PORT")
    env = {"DB_HOST": "localhost"}  # DB_PORT missing
    missing = check_missing(base_dir, "myapp", env)
    assert "DB_URL" in missing
    assert "DB_PORT" in missing["DB_URL"]
    assert "DB_HOST" not in missing.get("DB_URL", [])


def test_check_missing_returns_empty_when_all_present(base_dir):
    add_dependency(base_dir, "myapp", "DB_URL", "DB_HOST")
    env = {"DB_HOST": "localhost", "DB_URL": "postgres://localhost/db"}
    missing = check_missing(base_dir, "myapp", env)
    assert missing == {}
