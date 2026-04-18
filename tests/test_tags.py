"""Tests for envchain.tags module."""

import pytest
from pathlib import Path
from envchain.tags import (
    add_tag, remove_tag, get_tags, find_by_tag,
    list_all_tags, load_tags, save_tags
)


@pytest.fixture
def tag_dir(tmp_path):
    return str(tmp_path)


def test_load_tags_empty(tag_dir):
    assert load_tags("myvault", base_dir=tag_dir) == {}


def test_add_tag_creates_entry(tag_dir):
    add_tag("myvault", "API_KEY", "secret", base_dir=tag_dir)
    assert "secret" in get_tags("myvault", "API_KEY", base_dir=tag_dir)


def test_add_tag_no_duplicates(tag_dir):
    add_tag("myvault", "API_KEY", "secret", base_dir=tag_dir)
    add_tag("myvault", "API_KEY", "secret", base_dir=tag_dir)
    assert get_tags("myvault", "API_KEY", base_dir=tag_dir).count("secret") == 1


def test_add_multiple_tags(tag_dir):
    add_tag("myvault", "DB_PASS", "secret", base_dir=tag_dir)
    add_tag("myvault", "DB_PASS", "db", base_dir=tag_dir)
    tags = get_tags("myvault", "DB_PASS", base_dir=tag_dir)
    assert "secret" in tags
    assert "db" in tags


def test_remove_tag(tag_dir):
    add_tag("myvault", "TOKEN", "auth", base_dir=tag_dir)
    remove_tag("myvault", "TOKEN", "auth", base_dir=tag_dir)
    assert get_tags("myvault", "TOKEN", base_dir=tag_dir) == []


def test_remove_tag_cleans_empty_key(tag_dir):
    add_tag("myvault", "TOKEN", "auth", base_dir=tag_dir)
    remove_tag("myvault", "TOKEN", "auth", base_dir=tag_dir)
    tags = load_tags("myvault", base_dir=tag_dir)
    assert "TOKEN" not in tags


def test_remove_nonexistent_tag_no_error(tag_dir):
    remove_tag("myvault", "MISSING_KEY", "ghost", base_dir=tag_dir)


def test_find_by_tag(tag_dir):
    add_tag("myvault", "API_KEY", "secret", base_dir=tag_dir)
    add_tag("myvault", "DB_PASS", "secret", base_dir=tag_dir)
    add_tag("myvault", "LOG_LEVEL", "config", base_dir=tag_dir)
    result = find_by_tag("myvault", "secret", base_dir=tag_dir)
    assert set(result) == {"API_KEY", "DB_PASS"}


def test_find_by_tag_no_matches(tag_dir):
    assert find_by_tag("myvault", "nonexistent", base_dir=tag_dir) == []


def test_list_all_tags(tag_dir):
    add_tag("myvault", "API_KEY", "secret", base_dir=tag_dir)
    add_tag("myvault", "DB_PASS", "db", base_dir=tag_dir)
    add_tag("myvault", "TOKEN", "secret", base_dir=tag_dir)
    all_tags = list_all_tags("myvault", base_dir=tag_dir)
    assert all_tags == ["db", "secret"]


def test_get_tags_missing_key(tag_dir):
    assert get_tags("myvault", "NONEXISTENT", base_dir=tag_dir) == []
