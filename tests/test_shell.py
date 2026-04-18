"""Tests for envchain.shell module."""

import os
import pytest
from unittest.mock import patch

from envchain.shell import (
    detect_shell,
    format_exports,
    inject_into_env,
    _quote_posix,
    _quote_fish,
)


def test_detect_shell_from_env():
    with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
        assert detect_shell() == "bash"


def test_detect_shell_zsh():
    with patch.dict(os.environ, {"SHELL": "/usr/bin/zsh"}):
        assert detect_shell() == "zsh"


def test_detect_shell_unknown_falls_back_to_sh():
    with patch.dict(os.environ, {"SHELL": "/usr/bin/tcsh"}):
        assert detect_shell() == "sh"


def test_detect_shell_missing_falls_back_to_sh():
    env = {k: v for k, v in os.environ.items() if k != "SHELL"}
    with patch.dict(os.environ, env, clear=True):
        assert detect_shell() == "sh"


def test_format_exports_bash():
    variables = {"FOO": "bar", "BAZ": "qux"}
    result = format_exports(variables, shell="bash")
    assert "export FOO='bar';" in result
    assert "export BAZ='qux';" in result


def test_format_exports_fish():
    variables = {"MY_VAR": "hello world"}
    result = format_exports(variables, shell="fish")
    assert "set -x MY_VAR 'hello world';" in result


def test_format_exports_uses_detected_shell():
    with patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
        result = format_exports({"KEY": "value"})
    assert "export KEY='value';" in result


def test_quote_posix_simple():
    assert _quote_posix("hello") == "'hello'"


def test_quote_posix_with_single_quote():
    result = _quote_posix("it's")
    assert "'" not in result.strip("'"[0]) or "'\"'\"'" in result


def test_quote_posix_special_chars():
    result = _quote_posix("hello world")
    assert result == "'hello world'"


def test_quote_fish_simple():
    assert _quote_fish("value") == "'value'"


def test_inject_into_env():
    inject_into_env({"ENVCHAIN_TEST_VAR": "injected"})
    assert os.environ.get("ENVCHAIN_TEST_VAR") == "injected"
    del os.environ["ENVCHAIN_TEST_VAR"]
