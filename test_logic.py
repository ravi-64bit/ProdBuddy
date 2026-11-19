import pytest

import logic


def test_parse_tags_normalizes_and_deduplicates():
    assert logic.parse_tags(" Work, #home , WORK, , urgent ") == "work,home,urgent"
    assert logic.parse_tags(["#Ops", "ops", "Backend"]) == "ops,backend"
    assert logic.parse_tags(None) == ""


def test_parse_tags_rejects_non_text():
    with pytest.raises(ValueError):
        logic.parse_tags(123)


def test_format_duration():
    assert logic.format_duration(0) == "0s"
    assert logic.format_duration(45) == "45s"
    assert logic.format_duration(125) == "2m 05s"
    assert logic.format_duration(3665) == "1h 01m"
    assert logic.format_duration(-10) == "0s"


def test_valid_date():
    assert logic.valid_date("") is None
    assert logic.valid_date(None) is None
    assert logic.valid_date("2026-11-19") == "2026-11-19"
    with pytest.raises(ValueError):
        logic.valid_date("19-11-2026")
    with pytest.raises(ValueError):
        logic.valid_date("not-a-date")