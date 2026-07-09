import pytest

from agent.parsing import extract_json_object, extract_json_array


def test_extract_json_object():
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extract_json_object_from_markdown():
    assert extract_json_object('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_array():
    assert extract_json_array("[1, 2, 3]") == [1, 2, 3]


def test_extract_json_array_from_prose():
    assert extract_json_array("Plan:\n[1, 2, 3]") == [1, 2, 3]


def test_invalid_json_object_raises():
    with pytest.raises(ValueError):
        extract_json_object("no object here")


def test_invalid_json_array_raises():
    with pytest.raises(ValueError):
        extract_json_array("no array here")
