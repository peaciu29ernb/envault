"""Tests for envault.pipeline."""

import pytest

from envault.pipeline import Pipeline, PipelineError, build_pipeline


ENV = {"FOO": "hello", "BAR": "world"}


def upper_step(env):
    return {k: v.upper() for k, v in env.items()}


def append_step(env):
    return {k: v + "!" for k, v in env.items()}


def bad_step(env):
    raise ValueError("intentional error")


def non_dict_step(env):
    return "oops"


# --- construction ---

def test_pipeline_starts_empty():
    p = Pipeline()
    assert len(p) == 0
    assert p.step_names() == []


def test_add_step_returns_self():
    p = Pipeline()
    ret = p.add_step("up", upper_step)
    assert ret is p


def test_add_step_records_name():
    p = Pipeline()
    p.add_step("up", upper_step)
    assert "up" in p.step_names()


def test_add_non_callable_raises():
    p = Pipeline()
    with pytest.raises(TypeError):
        p.add_step("bad", "not_callable")


def test_remove_step_returns_true():
    p = Pipeline()
    p.add_step("up", upper_step)
    assert p.remove_step("up") is True
    assert len(p) == 0


def test_remove_missing_step_returns_false():
    p = Pipeline()
    assert p.remove_step("ghost") is False


# --- run ---

def test_run_empty_pipeline_returns_copy():
    p = Pipeline()
    result = p.run(ENV)
    assert result == ENV
    assert result is not ENV


def test_run_single_step():
    p = Pipeline()
    p.add_step("up", upper_step)
    result = p.run(ENV)
    assert result == {"FOO": "HELLO", "BAR": "WORLD"}


def test_run_multiple_steps_in_order():
    p = Pipeline()
    p.add_step("up", upper_step)
    p.add_step("append", append_step)
    result = p.run(ENV)
    assert result == {"FOO": "HELLO!", "BAR": "WORLD!"}


def test_run_step_raises_pipeline_error():
    p = Pipeline()
    p.add_step("bad", bad_step)
    with pytest.raises(PipelineError) as exc_info:
        p.run(ENV)
    assert exc_info.value.step_name == "bad"


def test_run_non_dict_step_raises_pipeline_error():
    p = Pipeline()
    p.add_step("nd", non_dict_step)
    with pytest.raises(PipelineError):
        p.run(ENV)


def test_pipeline_error_message_contains_step_name():
    err = PipelineError("mystep", "something went wrong")
    assert "mystep" in str(err)
    assert "something went wrong" in str(err)


# --- build_pipeline ---

def test_build_pipeline_creates_steps():
    p = build_pipeline("test", [{"name": "up", "fn": upper_step}])
    assert p.step_names() == ["up"]


def test_build_pipeline_empty_steps():
    p = build_pipeline("empty")
    assert len(p) == 0


def test_pipeline_repr_contains_name():
    p = Pipeline(name="mypipe")
    assert "mypipe" in repr(p)
