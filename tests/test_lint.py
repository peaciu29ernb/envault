"""Tests for envault.lint module."""

import pytest
from envault.lint import lint_env, format_lint_report, has_errors, LintWarning


def test_clean_env_no_warnings():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    warnings = lint_env(env)
    assert warnings == []


def test_invalid_key_name_error():
    env = {"123INVALID": "value"}
    warnings = lint_env(env)
    severities = [w.severity for w in warnings]
    assert "error" in severities
    assert any("POSIX" in w.message for w in warnings)


def test_lowercase_key_warning():
    env = {"my_var": "value"}
    warnings = lint_env(env)
    messages = [w.message for w in warnings]
    assert any("uppercase" in m for m in messages)


def test_empty_value_warning():
    env = {"EMPTY_VAR": ""}
    warnings = lint_env(env)
    assert any("empty" in w.message.lower() for w in warnings)


def test_long_value_warning():
    env = {"BIG_VAR": "x" * 1025}
    warnings = lint_env(env)
    assert any("long" in w.message.lower() for w in warnings)


def test_shell_special_chars_warning():
    env = {"CMD": "echo $HOME"}
    warnings = lint_env(env)
    assert any("shell special" in w.message for w in warnings)


def test_whitespace_value_warning():
    env = {"PADDED": "  value  "}
    warnings = lint_env(env)
    assert any("whitespace" in w.message for w in warnings)


def test_multiple_issues_same_key():
    # lowercase key + empty value
    env = {"my_empty": ""}
    warnings = lint_env(env)
    keys_with_warnings = [w.key for w in warnings]
    assert keys_with_warnings.count("my_empty") >= 2


def test_format_lint_report_no_issues():
    report = format_lint_report([])
    assert "No lint issues" in report


def test_format_lint_report_with_issues():
    warnings = [LintWarning("BAD_KEY", "Some issue.", "warning")]
    report = format_lint_report(warnings)
    assert "1 issue" in report
    assert "BAD_KEY" in report


def test_has_errors_true():
    warnings = [LintWarning("X", "bad", "error")]
    assert has_errors(warnings) is True


def test_has_errors_false_when_only_warnings():
    warnings = [LintWarning("X", "minor", "warning")]
    assert has_errors(warnings) is False


def test_has_errors_false_empty():
    assert has_errors([]) is False


def test_lint_warning_to_dict():
    w = LintWarning("MY_VAR", "Some message.", "warning")
    d = w.to_dict()
    assert d == {"key": "MY_VAR", "message": "Some message.", "severity": "warning"}


def test_lint_warning_repr():
    w = LintWarning("MY_VAR", "Issue.", "error")
    assert "ERROR" in repr(w)
    assert "MY_VAR" in repr(w)
