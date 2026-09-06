"""Tests for utils module."""

from levitan.utils import normalize_phone


def test_normalize_with_plus_seven():
    assert normalize_phone("+79186393030") == "79186393030"


def test_normalize_with_eight():
    assert normalize_phone("89186393030") == "79186393030"


def test_normalize_without_prefix():
    assert normalize_phone("9186393030") == "79186393030"


def test_normalize_with_brackets_and_dashes():
    assert normalize_phone("+7 (918) 639-30-30") == "79186393030"


def test_normalize_with_dashes_only():
    assert normalize_phone("8-918-639-30-30") == "79186393030"


def test_normalize_with_spaces():
    assert normalize_phone("+7 918 639 30 30") == "79186393030"


def test_normalize_short_number():
    assert normalize_phone("123") == ""


def test_normalize_empty():
    assert normalize_phone("") == ""


def test_normalize_none():
    assert normalize_phone(None) == ""


def test_normalize_already_normalized():
    assert normalize_phone("79186393030") == "79186393030"
