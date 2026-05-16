"""Tests for envault.flatten module."""

import pytest

from envault.flatten import FlattenError, expand_dict, flatten_dict, flatten_env


# ---------------------------------------------------------------------------
# flatten_dict
# ---------------------------------------------------------------------------

def test_flatten_dict_simple():
    data = {"HOST": "localhost", "PORT": "5432"}
    assert flatten_dict(data) == {"HOST": "localhost", "PORT": "5432"}


def test_flatten_dict_nested_one_level():
    data = {"db": {"host": "localhost", "port": "5432"}}
    result = flatten_dict(data)
    assert result == {"DB__HOST": "localhost", "DB__PORT": "5432"}


def test_flatten_dict_nested_two_levels():
    data = {"aws": {"s3": {"bucket": "my-bucket"}}}
    result = flatten_dict(data)
    assert result == {"AWS__S3__BUCKET": "my-bucket"}


def test_flatten_dict_upcases_keys():
    data = {"db": {"Host": "localhost"}}
    result = flatten_dict(data)
    assert "DB__HOST" in result


def test_flatten_dict_none_value_becomes_empty_string():
    data = {"KEY": None}
    assert flatten_dict(data) == {"KEY": ""}


def test_flatten_dict_bool_value_stringified():
    data = {"DEBUG": True}
    assert flatten_dict(data) == {"DEBUG": "True"}


def test_flatten_dict_int_value_stringified():
    data = {"PORT": 8080}
    assert flatten_dict(data) == {"PORT": "8080"}


def test_flatten_dict_custom_separator():
    data = {"db": {"host": "localhost"}}
    result = flatten_dict(data, separator="_")
    assert result == {"DB_HOST": "localhost"}


def test_flatten_dict_unsupported_value_raises():
    data = {"KEY": ["a", "b"]}
    with pytest.raises(FlattenError, match="Unsupported value type"):
        flatten_dict(data)


def test_flatten_dict_non_string_key_raises():
    with pytest.raises(FlattenError, match="All keys must be strings"):
        flatten_dict({1: "value"})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# expand_dict
# ---------------------------------------------------------------------------

def test_expand_dict_simple():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = expand_dict(env)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_expand_dict_one_level():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432"}
    result = expand_dict(env)
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_expand_dict_two_levels():
    env = {"AWS__S3__BUCKET": "my-bucket"}
    result = expand_dict(env)
    assert result == {"AWS": {"S3": {"BUCKET": "my-bucket"}}}


def test_expand_dict_custom_separator():
    env = {"DB_HOST": "localhost"}
    result = expand_dict(env, separator="_")
    assert result == {"DB": {"HOST": "localhost"}}


def test_expand_dict_conflict_scalar_then_dict_raises():
    env = {"DB": "value", "DB__HOST": "localhost"}
    with pytest.raises(FlattenError, match="Key conflict"):
        expand_dict(env)


# ---------------------------------------------------------------------------
# roundtrip
# ---------------------------------------------------------------------------

def test_flatten_expand_roundtrip():
    original = {"db": {"host": "localhost", "port": "5432"}, "debug": "true"}
    flat = flatten_dict(original)
    expanded = expand_dict(flat)
    # keys are upper-cased after roundtrip
    assert expanded["DB"]["HOST"] == "localhost"
    assert expanded["DB"]["PORT"] == "5432"
    assert expanded["DEBUG"] == "true"


def test_flatten_env_passthrough_for_flat_dict():
    env = {"KEY": "value", "OTHER": "data"}
    assert flatten_env(env) == {"KEY": "value", "OTHER": "DATA".replace("DATA", "data")}
