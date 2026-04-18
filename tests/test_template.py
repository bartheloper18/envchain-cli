"""Tests for envchain.template module."""

import pytest
import os
from envchain.template import render_template, find_placeholders, render_file


VARS = {"NAME": "Alice", "GREETING": "Hello", "PORT": "8080"}


def test_render_braced_placeholder():
    result = render_template("${GREETING}, ${NAME}!", VARS)
    assert result == "Hello, Alice!"


def test_render_unbraced_placeholder():
    result = render_template("$GREETING $NAME", VARS)
    assert result == "Hello Alice"


def test_render_mixed_placeholders():
    result = render_template("${GREETING}, $NAME on port $PORT", VARS)
    assert result == "Hello, Alice on port 8080"


def test_render_missing_placeholder_non_strict():
    result = render_template("Hello ${UNKNOWN}", VARS)
    assert "${UNKNOWN}" in result


def test_render_missing_placeholder_strict():
    with pytest.raises(KeyError, match="UNKNOWN"):
        render_template("Hello ${UNKNOWN}", VARS, strict=True)


def test_render_no_placeholders():
    result = render_template("plain text", VARS)
    assert result == "plain text"


def test_find_placeholders_braced():
    names = find_placeholders("${FOO} and ${BAR}")
    assert names == ["BAR", "FOO"]


def test_find_placeholders_unbraced():
    names = find_placeholders("$FOO $BAR $FOO")
    assert names == ["BAR", "FOO"]


def test_find_placeholders_empty():
    assert find_placeholders("no vars here") == []


def test_render_file(tmp_path):
    src = tmp_path / "tmpl.txt"
    dst = tmp_path / "out.txt"
    src.write_text("Host=${HOST} Port=${PORT}")
    render_file(str(src), str(dst), {"HOST": "localhost", "PORT": "5432"})
    assert dst.read_text() == "Host=localhost Port=5432"


def test_render_file_strict_missing(tmp_path):
    src = tmp_path / "tmpl.txt"
    src.write_text("${MISSING_VAR}")
    with pytest.raises(KeyError):
        render_file(str(src), str(tmp_path / "out.txt"), {}, strict=True)
